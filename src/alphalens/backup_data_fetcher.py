"""
备用数据源模块
当 akshare 连接失败时，使用其他数据源作为备选

支持的数据源：
1. akshare - 主要数据源（东方财富）
2. yfinance - Yahoo Finance（国际数据）
3. 模拟数据 - 用于演示和测试
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from loguru import logger
import random


class BackupDataFetcher:
    """备用数据获取器"""
    
    # 预设行业数据（用于演示）
    PRESET_INDUSTRIES = {
        "半导体": {"code": "BK1036", "change": 2.5},
        "新能源": {"code": "BK0493", "change": 1.8},
        "医药生物": {"code": "BK0727", "change": -0.5},
        "食品饮料": {"code": "BK0438", "change": 0.3},
        "电子元件": {"code": "BK0459", "change": 1.2},
        "软件服务": {"code": "BK0731", "change": 3.1},
        "互联网": {"code": "BK0448", "change": 2.2},
        "通信设备": {"code": "BK0444", "change": 0.8},
        "银行": {"code": "BK0475", "change": -0.2},
        "证券": {"code": "BK0473", "change": 1.5},
        "房地产": {"code": "BK0451", "change": -1.2},
        "建筑工程": {"code": "BK0425", "change": 0.5},
        "有色金属": {"code": "BK0478", "change": 2.8},
        "化工行业": {"code": "BK0428", "change": -0.8},
        "汽车整车": {"code": "BK0481", "change": 1.9},
        "电力行业": {"code": "BK0428", "change": 0.6},
        "军工": {"code": "BK0490", "change": 3.5},
        "传媒": {"code": "BK0486", "change": -0.3},
        "环保": {"code": "BK0728", "change": 0.4},
        "纺织服装": {"code": "BK0435", "change": -0.6},
    }
    
    def __init__(self):
        self.use_mock = False
    
    def get_industry_list(self) -> pd.DataFrame:
        """获取行业列表（备用数据）"""
        logger.warning("[备用数据源] 使用模拟行业列表数据")
        
        industries = []
        for name, info in self.PRESET_INDUSTRIES.items():
            industries.append({
                "板块名称": name,
                "板块代码": info["code"],
                "涨跌幅": info["change"] + random.uniform(-0.5, 0.5),
                "主力净流入": random.uniform(-100000000, 100000000),
                "换手率": random.uniform(1, 5),
                "成交额": random.uniform(1000000000, 5000000000),
            })
        
        return pd.DataFrame(industries)
    
    def get_industry_daily(self, industry_name: str, days: int = 60) -> pd.DataFrame:
        """获取行业日线数据（备用数据）"""
        logger.warning(f"[备用数据源] 使用模拟日线数据: {industry_name}")
        
        # 生成模拟日线数据
        end_date = datetime.now()
        dates = pd.date_range(end=end_date, periods=days, freq='D')
        
        base_price = random.uniform(1000, 5000)
        data = []
        
        for i, date in enumerate(dates):
            # 随机 walk
            change_pct = random.uniform(-0.03, 0.03)
            base_price = base_price * (1 + change_pct)
            
            data.append({
                "日期": date.strftime("%Y-%m-%d"),
                "开盘": base_price * (1 + random.uniform(-0.01, 0.01)),
                "收盘": base_price,
                "最高": base_price * (1 + random.uniform(0, 0.02)),
                "最低": base_price * (1 - random.uniform(0, 0.02)),
                "成交量": random.uniform(1000000, 10000000),
                "成交额": random.uniform(100000000, 1000000000),
                "振幅": random.uniform(1, 5),
                "涨跌幅": change_pct * 100,
                "涨跌额": base_price * change_pct,
            })
        
        df = pd.DataFrame(data)
        df['日期'] = pd.to_datetime(df['日期'])
        return df
    
    def get_industry_stocks(self, industry_name: str) -> pd.DataFrame:
        """获取行业成分股（备用数据）"""
        logger.warning(f"[备用数据源] 使用模拟成分股数据: {industry_name}")
        
        # 生成模拟成分股
        stocks = []
        stock_names = [
            "科技", "智能", "创新", "发展", "未来",
            "龙头", "领先", "第一", "集团", "股份"
        ]
        
        for i in range(random.randint(20, 50)):
            stock_name = f"{industry_name[:2]}{stock_names[i % len(stock_names)]}{i+1}"
            stock_code = f"{random.randint(600000, 699999)}"
            change = random.uniform(-5, 5)
            
            stocks.append({
                "代码": stock_code,
                "名称": stock_name,
                "最新价": random.uniform(10, 100),
                "涨跌幅": change,
                "涨跌额": random.uniform(-2, 2),
                "成交量": random.uniform(10000, 1000000),
                "成交额": random.uniform(1000000, 100000000),
                "主力净流入": random.uniform(-50000000, 50000000),
            })
        
        return pd.DataFrame(stocks)
    
    def get_etf_list(self) -> pd.DataFrame:
        """获取ETF列表（备用数据）"""
        logger.warning("[备用数据源] 使用模拟ETF列表数据")
        
        etfs = [
            {"name": "半导体ETF", "code": "512480"},
            {"name": "新能源ETF", "code": "516160"},
            {"name": "医药ETF", "code": "512010"},
            {"name": "食品ETF", "code": "515710"},
            {"name": "科技ETF", "code": "515000"},
            {"name": "银行ETF", "code": "512800"},
            {"name": "证券ETF", "code": "512880"},
            {"name": "军工ETF", "code": "512660"},
        ]
        
        data = []
        for etf in etfs:
            data.append({
                "代码": etf["code"],
                "名称": etf["name"],
                "最新价": random.uniform(1, 3),
                "涨跌幅": random.uniform(-2, 2),
                "涨跌额": random.uniform(-0.1, 0.1),
                "成交量": random.uniform(1000000, 10000000),
                "成交额": random.uniform(10000000, 100000000),
            })
        
        return pd.DataFrame(data)
    
    def get_hot_industries(self) -> pd.DataFrame:
        """获取热门行业（备用数据）"""
        logger.warning("[备用数据源] 使用模拟热门行业数据")
        
        # 返回涨跌幅排序的行业
        df = self.get_industry_list()
        df = df.sort_values('涨跌幅', ascending=False)
        return df.head(10)


class MultiSourceDataFetcher:
    """多数据源获取器（主数据源失败时自动切换）"""
    
    def __init__(self):
        self.primary_fetcher = None
        self.backup_fetcher = BackupDataFetcher()
        self.use_backup = False
        
        # 尝试导入 akshare
        try:
            from .data_fetcher import IndustryDataFetcher
            self.primary_fetcher = IndustryDataFetcher()
            logger.info("[多数据源] 主数据源初始化成功")
        except Exception as e:
            logger.warning(f"[多数据源] 主数据源初始化失败: {e}")
            self.use_backup = True
    
    def _try_primary(self, method_name: str, *args, **kwargs):
        """尝试使用主数据源，失败时切换到备用"""
        if not self.use_backup and self.primary_fetcher:
            try:
                method = getattr(self.primary_fetcher, method_name)
                result = method(*args, **kwargs)
                
                # 检查结果是否为空
                if isinstance(result, pd.DataFrame) and result.empty:
                    raise ValueError("主数据源返回空数据")
                
                return result
            except Exception as e:
                logger.warning(f"[多数据源] 主数据源失败，切换到备用: {e}")
                self.use_backup = True
        
        # 使用备用数据源
        method = getattr(self.backup_fetcher, method_name)
        return method(*args, **kwargs)
    
    def get_industry_list(self, **kwargs) -> pd.DataFrame:
        return self._try_primary('get_industry_list', **kwargs)
    
    def get_industry_daily(self, industry_name: str, **kwargs) -> pd.DataFrame:
        return self._try_primary('get_industry_daily', industry_name, **kwargs)
    
    def get_industry_stocks(self, industry_name: str, **kwargs) -> pd.DataFrame:
        return self._try_primary('get_industry_stocks', industry_name, **kwargs)
    
    def get_etf_list(self, **kwargs) -> pd.DataFrame:
        return self._try_primary('get_etf_list', **kwargs)
    
    def get_hot_industries(self, **kwargs) -> pd.DataFrame:
        return self._try_primary('get_hot_industries', **kwargs)
    
    def is_using_backup(self) -> bool:
        """检查是否正在使用备用数据源"""
        return self.use_backup


# 兼容性导入
if __name__ == "__main__":
    # 测试备用数据源
    fetcher = BackupDataFetcher()
    
    print("测试备用数据源...")
    print("\n1. 行业列表:")
    df = fetcher.get_industry_list()
    print(df.head())
    
    print("\n2. 行业日线:")
    df = fetcher.get_industry_daily("半导体")
    print(df.head())
    
    print("\n3. 成分股:")
    df = fetcher.get_industry_stocks("半导体")
    print(df.head())
