"""
Akshare 行业/板块/ETF基金数据获取模块
获取行业趋势、资金流向、ETF基金投资机会
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from loguru import logger
import re


# 行业名称映射（用户输入 -> 标准名称）
INDUSTRY_NAME_MAP = {
    "软件服务": "软件开发",
    "软件": "软件开发",
    "电力行业": "电力",
    "电力股": "电力",
    "新能源车": "新能源汽车",
    "新能源": "新能源",
    "半导体": "半导体",
    "芯片": "半导体",
    "医药": "医药生物",
    "医疗": "医疗服务",
    "消费": "消费",
    "食品": "食品饮料",
    "白酒": "白酒",
    "银行": "银行",
    "证券": "证券",
    "保险": "保险",
    "地产": "房地产",
    "军工": "国防军工",
    "通信": "通信设备",
    "计算机": "计算机应用",
}


class IndustryDataFetcher:
    """行业/板块数据获取器"""
    
    def __init__(self):
        self.cache: Dict = {}
        self.cache_ttl = 300  # 缓存5分钟
        self._industry_list_cache = None
    
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
    
    def get_industry_list(self) -> pd.DataFrame:
        """获取行业板块列表"""
        cache_key = "industry_list"
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        try:
            # 获取行业板块数据
            df = ak.stock_board_industry_name_em()
            self.cache[cache_key] = (df, datetime.now())
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
    
    def get_hot_industries(self) -> pd.DataFrame:
        """获取热门行业板块"""
        try:
            df = ak.stock_board_industry_name_em()
            
            # 按今日涨幅排序，获取热门行业
            if '涨跌幅' in df.columns:
                df = df.sort_values('涨跌幅', ascending=False)
            
            return df.head(10)
        except Exception as e:
            logger.error(f"获取热门行业失败: {e}")
            return pd.DataFrame()
    
    def get_etf_list(self) -> pd.DataFrame:
        """获取ETF基金列表"""
        cache_key = "etf_list"
        
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).seconds < self.cache_ttl:
                return cached_data
        
        try:
            # 获取全部ETF
            df = ak.fund_etf_spot_em()
            self.cache[cache_key] = (df, datetime.now())
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
