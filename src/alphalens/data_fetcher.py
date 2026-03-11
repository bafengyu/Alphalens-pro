"""
Akshare 行业/板块/ETF基金数据获取模块
获取行业趋势、资金流向、ETF基金投资机会

更新：添加每日数据源缓存机制
- 当天首次请求获取数据并存储
- 后续请求直接使用缓存数据
- 次日自动刷新
"""

import akshare as ak
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from loguru import logger
import re


# 行业名称映射（用户输入 -> 标准名称）
INDUSTRY_NAME_MAP = {
    # 软件与科技
    "软件服务": "软件开发",
    "软件": "软件开发",
    "互联网": "互联网服务",
    "计算机": "计算机应用",
    "通信": "通信设备",
    "通信设备": "通信设备",
    "电子元件": "电子",
    "电子": "电子",
    "芯片": "半导体",
    "半导体": "半导体",
    
    # 新能源与汽车
    "新能源车": "新能源汽车",
    "新能源": "新能源",
    "汽车整车": "汽车",
    "汽车": "汽车",
    
    # 医药医疗
    "医药": "医药生物",
    "医药生物": "医药生物",
    "医疗": "医疗服务",
    
    # 消费与食品
    "消费": "消费",
    "食品": "食品饮料",
    "食品饮料": "食品饮料",
    "白酒": "白酒",
    
    # 金融
    "银行": "银行",
    "证券": "证券",
    "保险": "保险",
    
    # 地产与建筑
    "地产": "房地产",
    "房地产": "房地产开发",
    "建筑工程": "建筑",
    "建筑": "建筑",
    
    # 工业与材料
    "军工": "国防军工",
    "电力行业": "电力",
    "电力": "电力",
    "电力股": "电力",
    "有色金属": "有色",
    "有色": "有色",
    "化工行业": "化工",
    "化工": "化工",
    
    # 其他
    "传媒": "文化传媒",
    "环保": "环境保护",
    "纺织服装": "纺织",
}


class DailyDataCache:
    """
    每日数据缓存管理器
    
    功能：
    1. 当天首次请求时从API获取数据并存储
    2. 后续请求直接使用缓存数据
    3. 次日自动识别并刷新数据
    4. 支持内存缓存和文件持久化
    """
    
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Dict] = {}
        self.today = datetime.now().strftime("%Y-%m-%d")
        
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 加载今日缓存（如果存在）
        self._load_today_cache()
    
    def _get_cache_file_path(self, data_type: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{self.today}_{data_type}.json")
    
    def _load_today_cache(self):
        """加载今日缓存数据"""
        cache_types = ["industry_list", "hot_industries", "etf_list"]
        
        for data_type in cache_types:
            cache_file = self._get_cache_file_path(data_type)
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        self.memory_cache[data_type] = json.load(f)
                    logger.info(f"[每日缓存] 加载 {data_type} 数据")
                except Exception as e:
                    logger.warning(f"[每日缓存] 加载 {data_type} 失败: {e}")
    
    def get(self, data_type: str, fetch_func: callable, force_refresh: bool = False):
        """
        获取数据（带每日缓存）
        
        Args:
            data_type: 数据类型标识
            fetch_func: 数据获取函数
            force_refresh: 强制刷新缓存
        
        Returns:
            数据对象
        """
        # 检查日期是否变化（新的一天）
        current_date = datetime.now().strftime("%Y-%m-%d")
        if current_date != self.today:
            logger.info(f"[每日缓存] 日期变化 {self.today} -> {current_date}，重置缓存")
            self.today = current_date
            self.memory_cache.clear()
        
        # 检查内存缓存
        if not force_refresh and data_type in self.memory_cache:
            logger.info(f"[每日缓存] 命中内存缓存: {data_type}")
            return self._deserialize_data(self.memory_cache[data_type])
        
        # 检查文件缓存
        cache_file = self._get_cache_file_path(data_type)
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.memory_cache[data_type] = json.load(f)
                logger.info(f"[每日缓存] 命中文件缓存: {data_type}")
                return self._deserialize_data(self.memory_cache[data_type])
            except Exception as e:
                logger.warning(f"[每日缓存] 读取文件缓存失败: {e}")
        
        # 首次请求：从API获取数据
        logger.info(f"[每日缓存] 首次获取 {data_type} 数据...")
        data = fetch_func()
        
        # 存储到缓存
        self._save_cache(data_type, data)
        
        return data
    
    def _save_cache(self, data_type: str, data):
        """保存数据到缓存"""
        try:
            # 序列化数据
            serialized = self._serialize_data(data)
            
            # 内存缓存
            self.memory_cache[data_type] = serialized
            
            # 文件持久化
            cache_file = self._get_cache_file_path(data_type)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(serialized, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[每日缓存] 已保存 {data_type} 数据")
        except Exception as e:
            logger.error(f"[每日缓存] 保存失败: {e}")
    
    def _serialize_data(self, data):
        """序列化数据（支持DataFrame）"""
        if isinstance(data, pd.DataFrame):
            return {
                "_type": "DataFrame",
                "data": data.to_dict(orient='records'),
                "columns": list(data.columns)
            }
        return data
    
    def _deserialize_data(self, data):
        """反序列化数据"""
        if isinstance(data, dict) and data.get("_type") == "DataFrame":
            return pd.DataFrame(data["data"], columns=data["columns"])
        return data
    
    def clear_cache(self):
        """清空所有缓存"""
        self.memory_cache.clear()
        
        # 删除缓存文件
        for filename in os.listdir(self.cache_dir):
            if filename.startswith(self.today):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except Exception as e:
                    logger.warning(f"删除缓存文件失败: {e}")
        
        logger.info("[每日缓存] 已清空今日缓存")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            "today": self.today,
            "memory_items": len(self.memory_cache),
            "cached_types": list(self.memory_cache.keys()),
            "cache_dir": self.cache_dir
        }


class IndustryDataFetcher:
    """行业/板块数据获取器（带每日缓存）"""
    
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache: Dict = {}
        self.cache_ttl = 300  # 缓存5分钟（保留原有短周期缓存）
        self._industry_list_cache = None
        
        # 每日数据缓存
        self.daily_cache = DailyDataCache(cache_dir)
    
    def _get_industry_list_cached(self) -> pd.DataFrame:
        """获取行业列表（带缓存）"""
        if self._industry_list_cache is None:
            try:
                self._industry_list_cache = ak.stock_board_industry_name_em()
            except Exception as e:
                logger.error(f"获取行业列表失败: {e}")
                self._industry_list_cache = pd.DataFrame()
        return self._industry_list_cache
    
    def _match_industry_name(self, industry_name: str) -> str:
        """
        根据输入的行业名称模糊匹配返回正确的板块名称
        
        Args:
            industry_name: 用户输入的行业名称
            
        Returns:
            匹配的板块名称
        """
        df = self._get_industry_list_cached()
        
        if df.empty:
            logger.warning(f"行业列表为空，直接使用名称: {industry_name}")
            return industry_name
        
        # 确保板块名称列存在
        if '板块名称' not in df.columns:
            logger.warning(f"行业列表缺少必要列，直接使用名称: {industry_name}")
            return industry_name
        
        # 1. 精确匹配
        exact_match = df[df['板块名称'] == industry_name]
        if not exact_match.empty:
            return exact_match.iloc[0]['板块名称']
        
        # 2. 使用预定义映射
        if industry_name in INDUSTRY_NAME_MAP:
            mapped_name = INDUSTRY_NAME_MAP[industry_name]
            mapped_match = df[df['板块名称'] == mapped_name]
            if not mapped_match.empty:
                logger.info(f"映射匹配: {industry_name} -> {mapped_name}")
                return mapped_name
        
        # 3. 模糊匹配 - 板块名称包含用户输入
        fuzzy_match = df[df['板块名称'].str.contains(industry_name, na=False)]
        if not fuzzy_match.empty:
            best_match = fuzzy_match.sort_values('板块名称').iloc[0]
            logger.info(f"模糊匹配: {industry_name} -> {best_match['板块名称']}")
            return best_match['板块名称']
        
        # 4. 反向匹配 - 用户输入包含在板块名称中
        for _, row in df.iterrows():
            if row['板块名称'] and industry_name in str(row['板块名称']):
                logger.info(f"反向匹配: {industry_name} -> {row['板块名称']}")
                return row['板块名称']
        
        # 5. 关键词匹配 - 提取关键词进行匹配
        keywords = industry_name.replace("行业", "").replace("板块", "").replace("股", "")
        if keywords != industry_name:
            keyword_match = df[df['板块名称'].str.contains(keywords, na=False)]
            if not keyword_match.empty:
                best_match = keyword_match.sort_values('板块名称').iloc[0]
                logger.info(f"关键词匹配: {industry_name} -> {best_match['板块名称']}")
                return best_match['板块名称']
        
        # 没找到匹配，返回原名称
        logger.warning(f"未找到匹配的行业: {industry_name}，直接使用")
        return industry_name
    
    def get_industry_list(self, use_daily_cache: bool = True) -> pd.DataFrame:
        """
        获取行业板块列表
        
        Args:
            use_daily_cache: 是否使用每日缓存（默认True）
        
        Returns:
            行业板块 DataFrame
        """
        if use_daily_cache:
            # 使用每日缓存：当天首次请求获取，后续使用缓存
            return self.daily_cache.get(
                "industry_list",
                lambda: self._fetch_industry_list()
            )
        else:
            # 使用短周期缓存（原有逻辑）
            cache_key = "industry_list"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    return cached_data
            return self._fetch_industry_list()
    
    def _fetch_industry_list(self) -> pd.DataFrame:
        """实际获取行业列表数据"""
        try:
            df = ak.stock_board_industry_name_em()
            self.cache["industry_list"] = (df, datetime.now())
            logger.info(f"成功获取 {len(df)} 个行业板块")
            return df
        except Exception as e:
            logger.error(f"获取行业列表失败: {e}")
            return pd.DataFrame()
    
    def get_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """
        获取指定行业的成分股
        
        Args:
            industry_name: 行业名称
            
        Returns:
            行业成分股 DataFrame
        """
        try:
            # 模糊匹配获取正确的板块名称
            matched_name = self._match_industry_name(industry_name)
            df = ak.stock_board_industry_cons_em(symbol=matched_name)
            logger.info(f"获取行业 {industry_name}({matched_name}) 成功，共 {len(df)} 只股票")
            return df
        except Exception as e:
            logger.error(f"获取行业成分股失败: {e}")
            return pd.DataFrame()
    
    def get_industry_daily(self, industry_name: str, days: int = 60) -> pd.DataFrame:
        """
        获取行业日线行情
        
        Args:
            industry_name: 行业名称
            days: 天数
            
        Returns:
            行业日线 DataFrame
        """
        try:
            # 模糊匹配获取正确的板块名称
            matched_name = self._match_industry_name(industry_name)
            df = ak.stock_board_industry_hist_em(symbol=matched_name)
            
            if df is not None and not df.empty:
                # 转换日期格式
                if '日期' in df.columns:
                    df['日期'] = pd.to_datetime(df['日期'])
                    # 截取最近的数据
                    df = df.tail(days)
            
            logger.info(f"获取行业 {industry_name}({matched_name}) 日线成功，共 {len(df)} 条")
            return df
        except Exception as e:
            logger.error(f"获取行业日线失败: {e}")
            return pd.DataFrame()
    
    def get_industry_fund_flow(self, industry_name: str) -> pd.DataFrame:
        """
        获取行业资金流向
        
        Args:
            industry_name: 行业名称
            
        Returns:
            资金流向 DataFrame
        """
        try:
            # 模糊匹配获取正确的板块名称
            matched_name = self._match_industry_name(industry_name)
            # 使用板块名称获取资金流向
            df = ak.stock_fund_flow_industry(symbol=matched_name)
            logger.info(f"获取行业资金流向成功: {len(df)} 条")
            return df
        except Exception as e:
            logger.warning(f"获取行业资金流向失败（可忽略）: {e}")
            # 返回空DataFrame而不是崩溃
            return pd.DataFrame()
    
    def get_hot_industries(self, use_daily_cache: bool = True) -> pd.DataFrame:
        """
        获取热门行业板块
        
        Args:
            use_daily_cache: 是否使用每日缓存（默认True）
        """
        if use_daily_cache:
            return self.daily_cache.get(
                "hot_industries",
                lambda: self._fetch_hot_industries()
            )
        else:
            return self._fetch_hot_industries()
    
    def _fetch_hot_industries(self) -> pd.DataFrame:
        """实际获取热门行业数据"""
        try:
            df = ak.stock_board_industry_name_em()
            
            # 按今日涨幅排序，获取热门行业
            if '涨跌幅' in df.columns:
                df = df.sort_values('涨跌幅', ascending=False)
            
            return df.head(10)
        except Exception as e:
            logger.error(f"获取热门行业失败: {e}")
            return pd.DataFrame()
    
    def get_etf_list(self, use_daily_cache: bool = True) -> pd.DataFrame:
        """
        获取ETF基金列表
        
        Args:
            use_daily_cache: 是否使用每日缓存（默认True）
        """
        if use_daily_cache:
            return self.daily_cache.get(
                "etf_list",
                lambda: self._fetch_etf_list()
            )
        else:
            # 使用短周期缓存
            cache_key = "etf_list"
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).seconds < self.cache_ttl:
                    return cached_data
            return self._fetch_etf_list()
    
    def _fetch_etf_list(self) -> pd.DataFrame:
        """实际获取ETF列表数据"""
        try:
            df = ak.fund_etf_spot_em()
            self.cache["etf_list"] = (df, datetime.now())
            logger.info(f"成功获取 {len(df)} 只ETF")
            return df
        except Exception as e:
            logger.error(f"获取ETF列表失败: {e}")
            return pd.DataFrame()
    
    def get_industry_etfs(self, industry_name: str) -> pd.DataFrame:
        """
        获取相关行业的ETF基金
        
        Args:
            industry_name: 行业名称
            
        Returns:
            相关ETF列表
        """
        etf_df = self.get_etf_list()
        
        if etf_df.empty:
            return pd.DataFrame()
        
        # 根据行业名称匹配ETF
        keywords = self._get_industry_keywords(industry_name)
        
        matched_etfs = pd.DataFrame()
        for keyword in keywords:
            mask = etf_df['名称'].str.contains(keyword, case=False, na=False)
            matched_etfs = pd.concat([matched_etfs, etf_df[mask]])
        
        # 去重
        if not matched_etfs.empty:
            matched_etfs = matched_etfs.drop_duplicates(subset=['代码'])
        
        return matched_etfs
    
    def _get_industry_keywords(self, industry_name: str) -> List[str]:
        """获取行业的关键词用于匹配ETF"""
        keywords_map = {
            "半导体": ["半导体", "芯片", "集成电路"],
            "新能源": ["新能源", "光伏", "锂电", "电动车", "电池"],
            "医药": ["医药", "医疗", "生物", "中药"],
            "消费": ["消费", "食品", "饮料", "家电", "纺织"],
            "金融": ["金融", "银行", "保险", "证券"],
            "科技": ["科技", "TMT", "计算机", "软件"],
            "军工": ["军工", "国防", "航天", "航空"],
            "房地产": ["房地产", "地产", "建材", "家居"],
            "基建": ["基建", "工程", "建筑", "钢铁", "水泥"],
            "互联网": ["互联网", "传媒", "游戏", "电商"],
            "新能源车": ["新能源车", "智能车", "汽车"],
            "电力": ["电力", "电网", "水电", "风电", "核电"],
            "有色": ["有色", "金属", "铜", "铝", "稀土"],
            "化工": ["化工", "新材料", "石化"],
        }
        
        return keywords_map.get(industry_name, [industry_name])
    
    def analyze_industry_trend(self, industry_name: str) -> Dict:
        """
        分析行业趋势
        
        Args:
            industry_name: 行业名称
            
        Returns:
            行业分析结果字典
        """
        result = {
            "industry_name": industry_name,
            "stocks_count": 0,
            "avg_change": 0.0,
            "up_count": 0,
            "down_count": 0,
            "main_inflow": 0.0,
            "hot_rank": 0,
            "recommendation": "",
        }
        
        try:
            # 获取行业成分股
            stocks_df = self.get_industry_stocks(industry_name)
            if not stocks_df.empty:
                result["stocks_count"] = len(stocks_df)
                
                # 统计涨跌
                if '涨跌幅' in stocks_df.columns:
                    result["up_count"] = len(stocks_df[stocks_df['涨跌幅'] > 0])
                    result["down_count"] = len(stocks_df[stocks_df['涨跌幅'] < 0])
                    result["avg_change"] = stocks_df['涨跌幅'].mean()
            
            # 获取资金流向
            fund_df = self.get_industry_fund_flow(industry_name)
            if not fund_df.empty:
                if '主力净流入-净额' in fund_df.columns:
                    result["main_inflow"] = fund_df['主力净流入-净额'].sum()
            
            # 生成推荐
            result["recommendation"] = self._generate_recommendation(result)
            
        except Exception as e:
            logger.error(f"分析行业趋势失败: {e}")
        
        return result
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        """基于分析结果生成推荐"""
        avg_change = analysis.get("avg_change", 0)
        main_inflow = analysis.get("main_inflow", 0)
        up_ratio = analysis.get("up_count", 0) / max(analysis.get("stocks_count", 1), 1)
        
        # 逻辑判断
        if avg_change > 3 and main_inflow > 0 and up_ratio > 0.7:
            return "强势买入"
        elif avg_change > 1 and main_inflow > 0:
            return "建议关注"
        elif avg_change < -3 and main_inflow < 0:
            return "注意风险"
        elif avg_change < -1:
            return "观望为主"
        else:
            return "中性持有"
    
    # ==================== 每日缓存管理方法 ====================
    
    def clear_daily_cache(self):
        """清空每日数据缓存"""
        self.daily_cache.clear_cache()
    
    def get_daily_cache_stats(self) -> Dict:
        """获取每日缓存统计信息"""
        return self.daily_cache.get_cache_stats()
    
    def refresh_daily_cache(self, data_type: str = None):
        """
        强制刷新每日缓存
        
        Args:
            data_type: 指定刷新类型（industry_list/hot_industries/etf_list），
                      为None则刷新所有
        """
        if data_type:
            logger.info(f"[每日缓存] 强制刷新 {data_type}")
            if data_type == "industry_list":
                self._fetch_industry_list()
            elif data_type == "hot_industries":
                self._fetch_hot_industries()
            elif data_type == "etf_list":
                self._fetch_etf_list()
        else:
            logger.info("[每日缓存] 强制刷新所有数据")
            self._fetch_industry_list()
            self._fetch_hot_industries()
            self._fetch_etf_list()


def format_industry_data_for_llm(industry_name: str, analysis: Dict, 
                                  etf_df: pd.DataFrame, daily_df: pd.DataFrame) -> str:
    """
    格式化行业数据，供 LLM 分析使用
    """
    lines = [
        "=== 行业分析数据 ===",
        f"行业名称: {industry_name}",
        "",
        "=== 行业整体表现 ===",
        f"成分股数量: {analysis.get('stocks_count', 'N/A')}",
        f"平均涨跌幅: {analysis.get('avg_change', 0):.2f}%",
        f"上涨股票数: {analysis.get('up_count', 0)}",
        f"下跌股票数: {analysis.get('down_count', 0)}",
        f"主力净流入: {analysis.get('main_inflow', 0):,.0f}",
        f"综合建议: {analysis.get('recommendation', 'N/A')}",
    ]
    
    # 添加ETF信息
    if not etf_df.empty:
        lines.extend([
            "",
            "=== 相关ETF基金 ===",
        ])
        for _, etf in etf_df.head(5).iterrows():
            name = etf.get('名称', '')
            price = etf.get('最新价', 0)
            change = etf.get('涨跌幅', 0)
            lines.append(f"- {name}: {price:.2f} ({change:+.2f}%)")
    
    # 添加近期走势
    if not daily_df.empty:
        latest = daily_df.iloc[-1] if len(daily_df) > 0 else None
        if latest is not None:
            lines.extend([
                "",
                "=== 近期走势 ===",
                f"最新收盘: {latest.get('收盘', 'N/A')}",
                f"近期最高: {daily_df['最高'].max() if '最高' in daily_df.columns else 'N/A'}",
                f"近期最低: {daily_df['最低'].min() if '最低' in daily_df.columns else 'N/A'}",
            ])
    
    return "\n".join(lines)


# 兼容旧代码
StockDataFetcher = IndustryDataFetcher
