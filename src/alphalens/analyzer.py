"""
股票分析引擎
整合数据获取和 LLM 分析，提供完整的股票分析流程
"""

from typing import Optional, Dict, List
import pandas as pd
from loguru import logger

from .data_fetcher import IndustryDataFetcher, format_industry_data_for_llm
from .llm_client import LLMClient, DecisionSignal, get_llm_client


class IndustryAnalyzer:
    """股票分析引擎"""
    
    def __init__(self):
        self.data_fetcher = IndustryDataFetcher()
        self._llm_client = None
    
    @property
    def llm_client(self):
        """延迟初始化 LLM 客户端，确保环境变量已加载"""
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client
        
    def analyze(self, industry_name: str, use_llm: bool = True) -> Dict:
        """
        分析单个行业
        
        Args:
            industry_name: 行业名称
            use_llm: 是否使用 LLM 分析
            
        Returns:
            分析结果字典
        """
        logger.info(f"开始分析行业: {industry_name}")
        
        result = {
            "industry_name": industry_name,
            "industry_analysis": None,
            "etf_list": None,
            "daily_data": None,
            "llm_signal": None,
            "error": None
        }
        
        try:
            # 1. 分析行业趋势
            analysis = self.data_fetcher.analyze_industry_trend(industry_name)
            result["industry_analysis"] = analysis
            
            # 2. 获取相关ETF列表
            etf_df = self.data_fetcher.get_industry_etfs(industry_name)
            result["etf_list"] = etf_df
            
            # 3. 获取行业日线数据
            daily_df = self.data_fetcher.get_industry_daily(industry_name, 60)
            result["daily_data"] = daily_df
            
            # 4. LLM 深度分析
            if use_llm:
                industry_data_str = format_industry_data_for_llm(
                    industry_name,
                    analysis,
                    etf_df,
                    daily_df
                )
                
                signal = self.llm_client.analyze_industry(
                    industry_name=industry_name,
                    industry_data=industry_data_str
                )
                result["llm_signal"] = signal
            
            logger.info(f"行业分析完成: {industry_name}")
            
        except Exception as e:
            logger.error(f"行业分析异常: {e}")
            result["error"] = str(e)
        
        return result
    
    def get_hot_industries(self, top_n: int = 10) -> pd.DataFrame:
        """
        获取热门行业板块
        
        Args:
            top_n: 返回数量
            
        Returns:
            热门行业 DataFrame
        """
        try:
            df = self.data_fetcher.get_hot_industries()
            return df.head(top_n)
        except Exception as e:
            logger.error(f"获取热门行业失败: {e}")
            return pd.DataFrame()
    
    def get_ai_recommendations(self, industries: List[str] = None) -> List[Dict]:
        """
        获取AI推荐行业（建议买入/定投的行业）
        
        Args:
            industries: 行业列表，默认分析热门行业
            
        Returns:
            推荐行业列表
        """
        if industries is None:
            # 默认分析热门行业
            hot = self.get_hot_industries(10)
            if not hot.empty:
                industries = hot['板块名称'].tolist()[:10]
            else:
                industries = ["半导体", "新能源", "医药生物", "食品饮料", "电子元件"]
        
        recommendations = []
        
        for industry in industries:
            try:
                result = self.analyze(industry, use_llm=True)
                signal = result.get('llm_signal')
                
                if signal and signal.decision:
                    # 只推荐建议买入/定投/关注的行业
                    if any(keyword in signal.decision for keyword in ["买入", "定投", "关注", "增持", "配置"]):
                        recommendations.append({
                            "industry": industry,
                            "decision": signal.decision,
                            "confidence": signal.confidence,
                            "reasoning": signal.reasoning[:200] if signal.reasoning else "",
                            "etf_list": result.get('etf_list'),
                            "analysis": result.get('industry_analysis', {})
                        })
            except Exception as e:
                logger.warning(f"分析行业 {industry} 失败: {e}")
                continue
        
        # 按置信度排序
        recommendations.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return recommendations[:5]  # 最多返回5个推荐
    
    def get_all_industries(self) -> List[str]:
        """
        获取所有行业名称
        
        Returns:
            行业名称列表
        """
        try:
            df = self.data_fetcher.get_industry_list()
            if not df.empty and '板块名称' in df.columns:
                return df['板块名称'].tolist()
        except Exception as e:
            logger.error(f"获取行业列表失败: {e}")
        
        # 返回常用行业作为备用
        return [
            "半导体", "新能源", "医药生物", "食品饮料", "电子元件",
            "软件服务", "互联网", "通信设备", "银行", "证券",
            "房地产", "建筑工程", "有色金属", "化工行业", "汽车整车",
            "电力行业", "军工", "传媒", "环保", "纺织服装"
        ]


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算技术指标
    
    Args:
        df: 日线 DataFrame
        
    Returns:
        添加技术指标后的 DataFrame
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # 移动平均线
    df['MA5'] = df['收盘'].rolling(5).mean()
    df['MA10'] = df['收盘'].rolling(10).mean()
    df['MA20'] = df['收盘'].rolling(20).mean()
    df['MA60'] = df['收盘'].rolling(60).mean()
    
    # MACD
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['SIGNAL'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['HIST'] = df['MACD'] - df['SIGNAL']
    
    # RSI
    delta = df['收盘'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 布林带
    df['BB_MID'] = df['收盘'].rolling(20).mean()
    df['BB_STD'] = df['收盘'].rolling(20).std()
    df['BB_UPPER'] = df['BB_MID'] + 2 * df['BB_STD']
    df['BB_LOWER'] = df['BB_MID'] - 2 * df['BB_STD']
    
    return df


def generate_trading_signals(df: pd.DataFrame) -> List[Dict]:
    """
    生成交易信号
    
    Args:
        df: 带技术指标的 DataFrame
        
    Returns:
        信号列表
    """
    signals = []
    
    if df.empty or len(df) < 20:
        return signals
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    # MA 金叉/死叉
    if prev['MA5'] <= prev['MA20'] and latest['MA5'] > latest['MA20']:
        signals.append({
            "type": "MA_CROSS_UP",
            "name": "MA5 上穿 MA20 - 金叉",
            "action": "买入信号"
        })
    elif prev['MA5'] >= prev['MA20'] and latest['MA5'] < latest['MA20']:
        signals.append({
            "type": "MA_CROSS_DOWN", 
            "name": "MA5 下穿 MA20 - 死叉",
            "action": "卖出信号"
        })
    
    # RSI 超买超卖
    if latest['RSI'] < 30:
        signals.append({
            "type": "RSI_OVERSOLD",
            "name": f"RSI = {latest['RSI']:.1f}",
            "action": "超卖，可能反弹"
        })
    elif latest['RSI'] > 70:
        signals.append({
            "type": "RSI_OVERBOUGHT",
            "name": f"RSI = {latest['RSI']:.1f}",
            "action": "超买，可能回调"
        })
    
    # MACD 金叉死叉
    if prev['MACD'] <= prev['SIGNAL'] and latest['MACD'] > latest['SIGNAL']:
        signals.append({
            "type": "MACD_GOLDEN",
            "name": "MACD 金叉",
            "action": "买入信号"
        })
    elif prev['MACD'] >= prev['SIGNAL'] and latest['MACD'] < latest['SIGNAL']:
        signals.append({
            "type": "MACD_DEAD",
            "name": "MACD 死叉",
            "action": "卖出信号"
        })
    
    # 突破布林带上轨
    if latest['收盘'] > latest['BB_UPPER']:
        signals.append({
            "type": "BB_BREAK_UP",
            "name": "突破布林上轨",
            "action": "强势信号，注意回调"
        })
    elif latest['收盘'] < latest['BB_LOWER']:
        signals.append({
            "type": "BB_BREAK_DOWN",
            "name": "跌破布林下轨",
            "action": "超卖，可能反弹"
        })
    
    return signals


if __name__ == "__main__":
    # 测试
    analyzer = StockAnalyzer()
    result = analyzer.analyze("000001")
    print(f"股票: {result['stock_name']}")
    if result['llm_signal']:
        print(f"决策: {result['llm_signal'].decision}")
        print(f"置信度: {result['llm_signal'].confidence}")
