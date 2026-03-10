"""
大模型客户端
支持多种 AI API：DeepSeek / 阿里云百炼(通义千问) / 火山引擎(豆包) / 腾讯云(混元)
思维链推理，输出带温度的决策信号
"""

import os
from typing import Optional
from openai import OpenAI
from loguru import logger
from pydantic import BaseModel


# 支持的模型类型
class ModelType:
    DEEPSEEK = "deepseek"
    DASHSCOPE = "dashscope"  # 阿里云百炼-通义千问
    ARK = "ark"  # 火山引擎-豆包
    TENCENT = "tencent"  # 腾讯云-混元


# 各模型配置
MODEL_CONFIGS = {
    ModelType.DEEPSEEK: {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-chat",
    },
    ModelType.DASHSCOPE: {
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "model": "qwen-plus",
    },
    ModelType.ARK: {
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "model": "doubao-lite",
    },
    ModelType.TENCENT: {
        "base_url": "https://hunyuan.tencentcloudapi.com",
        "model": "hunyuan-latest",
    },
}


# 机构操盘手思维链模板（个股分析）
TRADER_THINKING_CHAIN = """
你是一位有20年经验的资深机构操盘手，管理资产超过10亿。你的操盘风格：
1. 注重基本面与技术面的共振
2. 强调资金流向是股价涨跌的核心动力
3. 擅长识别主力的吸筹、拉升、出货阶段
4. 重视成交量与价格的关系

请按照以下思维链分析股票：

## 第一步：基本面审视
- 行业地位与景气度
- 近期是否有业绩拐点或政策利好

## 第二步：资金面分析
- 主力资金是否持续净流入
- 成交量是否出现异动
- 资金入场时机是否合适

## 第三步：技术面判断
- 当前位置处于上涨趋势还是下跌趋势
- 支撑位和压力位在哪里
- 是否有标志性K线形态

## 第四步：综合决策
结合以上分析，给出明确的操作建议

## 输出格式要求：
1. 必须包含"操作建议"章节
2. 建议要明确具体（买入/卖出/持有/锁仓/加仓/减仓）
3. 说明你的推理逻辑
4. 提示风险点
"""


# 行业/基金分析思维链
INDUSTRY_THINKING_CHAIN = """
你是一位有15年经验的资深行业研究员，擅长发掘行业趋势和基金投资机会。你的分析风格：
1. 宏观视角：关注政策导向和经济发展周期
2. 资金流向：追踪机构资金布局方向
3. 估值分析：判断行业和ETF的估值合理性
4. 轮动规律：把握市场风格切换规律

请按照以下思维链分析行业及ETF投资机会：

## 第一步：行业景气度分析
- 行业发展阶段（导入期/成长期/成熟期/衰退期）
- 政策支持力度和产业趋势
- 供需格局和竞争壁垒

## 第二步：资金面分析
- 主力资金是否持续流入该行业
- 机构持仓变化趋势
- 北向资金/融资融券动向

## 第三步：估值与性价比
- 当前估值在历史水位
- 与其他行业相比的性价比
- ETF的溢价率和流动性

## 第四步：投资建议
结合以上分析，给出具体的ETF投资建议

## 输出格式要求：
1. 必须包含"操作建议"章节
2. 建议要明确具体（如：建议买入XXETF、建议定投、建议观望等）
3. 说明你的推理逻辑
4. 提示风险点和止盈止损建议
"""


class DecisionSignal(BaseModel):
    """决策信号模型"""
    stock_code: str
    stock_name: str
    decision: str  # 买入/卖出/持有/锁仓/加仓/减仓/观望
    confidence: float  # 置信度 0-1
    reasoning: str  # 推理过程
    risk_warning: str  # 风险提示
    support_level: str  # 支撑位
    resistance_level: str  # 压力位
    timestamp: str


class LLMClient:
    """通用大模型客户端（支持多种API）"""
    
    def __init__(self, model_type: str = ModelType.DEEPSEEK, 
                 api_key: Optional[str] = None, 
                 model: Optional[str] = None):
        """
        初始化大模型客户端
        
        Args:
            model_type: 模型类型 (deepseek/dashscope/ark/tencent)
            api_key: API Key，默认从环境变量读取
            model: 模型名称，默认使用配置中的模型
        """
        config = MODEL_CONFIGS.get(model_type, MODEL_CONFIGS[ModelType.DEEPSEEK])
        
        # 根据模型类型获取 API Key
        if model_type == ModelType.DEEPSEEK:
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = os.getenv("DEEPSEEK_BASE_URL", config["base_url"])
        elif model_type == ModelType.DASHSCOPE:
            self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
            self.base_url = os.getenv("DASHSCOPE_BASE_URL", config["base_url"])
        elif model_type == ModelType.ARK:
            self.api_key = api_key or os.getenv("ARK_API_KEY")
            self.base_url = os.getenv("ARK_BASE_URL", config["base_url"])
        else:
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = config["base_url"]
        
        if not self.api_key:
            logger.warning(f"未设置 {model_type} API Key，将仅提供技术分析")
            # 不在这里初始化 client，延迟到实际调用时检查
            self.client = None
            return
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.model = model or config["model"]
        self.model_type = model_type
        
        logger.info(f"初始化 {model_type} 客户端，模型: {self.model}")
    
    # 兼容旧接口
    @staticmethod
    def create_deepseek(api_key: Optional[str] = None):
        """创建 DeepSeek 客户端"""
        return LLMClient(ModelType.DEEPSEEK, api_key)
    
    @staticmethod
    def create_dashscope(api_key: Optional[str] = None):
        """创建阿里云百炼(通义千问)客户端"""
        return LLMClient(ModelType.DASHSCOPE, api_key)
    
    @staticmethod
    def create_ark(api_key: Optional[str] = None):
        """创建火山引擎(豆包)客户端"""
        return LLMClient(ModelType.ARK, api_key)
    
    @staticmethod
    def create_tencent(secret_id: Optional[str] = None, secret_key: Optional[str] = None):
        """创建腾讯云(混元)客户端"""
        return LLMClient(ModelType.TENCENT, secret_key)  # 腾讯云使用 SecretKey 作为 api_key
        
    def analyze_stock(self, stock_code: str, stock_name: str, 
                     stock_data: str, thinking_chain: str = TRADER_THINKING_CHAIN) -> DecisionSignal:
        """
        使用 LLM 分析股票
        
        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            stock_data: 格式化后的股票数据
            thinking_chain: 思维链提示词
            
        Returns:
            DecisionSignal 决策信号
        """
        # 检查是否已配置 API Key
        if self.client is None:
            return self._no_api_key_signal(stock_code, stock_name)
        
        prompt = f"""
{thinking_chain}

=== 待分析股票 ===
股票代码: {stock_code}
股票名称: {stock_name}

{stock_data}

请按照思维链分析，并给出最终决策。
"""
        
        try:
            logger.info(f"调用 DeepSeek 分析股票: {stock_code}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一位专业的股票分析师，擅长结合基本面、资金面、技术面进行深度分析。你的回复要专业、严谨，同时要有温度，直接给出明确的操作建议。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            
            # 解析决策信号
            signal = self._parse_signal(stock_code, stock_name, content)
            
            logger.info(f"分析完成: {stock_code} -> {signal.decision} (置信度: {signal.confidence})")
            
            return signal
            
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            return self._error_signal(stock_code, stock_name, str(e))
    
    def analyze_industry(self, industry_name: str, industry_data: str) -> DecisionSignal:
        """
        使用 LLM 分析行业及ETF投资机会
        
        Args:
            industry_name: 行业名称
            industry_data: 格式化后的行业数据
            
        Returns:
            DecisionSignal 决策信号
        """
        # 检查是否已配置 API Key
        if self.client is None:
            return self._no_api_key_signal(industry_name, industry_name)
        
        prompt = f"""
{INDUSTRY_THINKING_CHAIN}

=== 待分析行业 ===
行业名称: {industry_name}

{industry_data}

请按照思维链分析，并给出最终的投资建议。
"""
        
        try:
            logger.info(f"调用 LLM 分析行业: {industry_name}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一位专业的行业研究员和基金分析师，擅长发掘行业趋势和ETF投资机会。你的回复要专业、严谨，直接给出明确的投资建议，包括具体的ETF代码或名称。"
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            content = response.choices[0].message.content
            
            # 解析决策信号
            signal = self._parse_industry_signal(industry_name, content)
            
            logger.info(f"行业分析完成: {industry_name} -> {signal.decision}")
            
            return signal
            
        except Exception as e:
            logger.error(f"LLM 行业分析调用失败: {e}")
            return self._error_signal(industry_name, industry_name, str(e))
    
    def _parse_industry_signal(self, industry_name: str, content: str) -> DecisionSignal:
        """解析 AI 返回的行业分析内容"""
        from datetime import datetime
        
        # 提取决策关键词
        decision = "观望"
        confidence = 0.5
        
        decision_keywords = {
            "建议买入": ["建议买入", "推荐买入", "可以买入", "建议建仓", "推荐配置"],
            "建议定投": ["建议定投", "可以定投", "建议分批", "分批买入"],
            "建议关注": ["建议关注", "可以关注", "值得关注", "重点关注"],
            "观望": ["观望", "等待", "暂不推荐", "谨慎"],
            "建议减仓": ["建议减仓", "可以减仓", "部分获利", "注意风险"],
            "建议卖出": ["建议卖出", "建议清仓", "注意回避"],
        }
        
        for dec, keywords in decision_keywords.items():
            for kw in keywords:
                if kw in content:
                    decision = dec
                    break
            if decision != "观望":
                break
        
        # 提取置信度
        import re
        confidence_match = re.search(r'(\d{1,2})%', content)
        if confidence_match:
            confidence = int(confidence_match.group(1)) / 100
        
        # 提取ETF推荐
        etf_match = re.search(r'ETF[：:]\s*([^\n]+)', content)
        etf_recommend = etf_match.group(1) if etf_match else "待分析"
        
        return DecisionSignal(
            stock_code=industry_name,
            stock_name=etf_recommend,  # 复用字段存储ETF推荐
            decision=decision,
            confidence=confidence,
            reasoning=content[:1000],
            risk_warning="投资有风险，入市需谨慎",
            support_level="N/A",
            resistance_level="N/A",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _parse_signal(self, stock_code: str, stock_name: str, content: str) -> DecisionSignal:
        """解析 AI 返回的内容，提取决策信号"""
        from datetime import datetime
        
        # 提取决策关键词
        content_upper = content.upper()
        decision = "观望"
        confidence = 0.5
        
        decision_keywords = {
            "买入": ["买入", "建仓", "买进", "可买", "推荐买入"],
            "加仓": ["加仓", "增仓", "补仓", "可以加"],
            "锁仓": ["锁仓", "持有", "继续持有", "维持持有"],
            "减仓": ["减仓", "部分获利", "可适当减"],
            "卖出": ["卖出", "清仓", "离场", "建议卖出"],
        }
        
        for dec, keywords in decision_keywords.items():
            for kw in keywords:
                if kw in content:
                    decision = dec
                    break
            if decision != "观望":
                break
        
        # 提取置信度
        import re
        confidence_match = re.search(r'(\d{1,2})%', content)
        if confidence_match:
            confidence = int(confidence_match.group(1)) / 100
        
        # 提取支撑位和压力位
        support_match = re.search(r'支撑[位价]*[:：]?\s*(\d+\.?\d*)', content)
        support = support_match.group(1) if support_match else "待分析"
        
        resistance_match = re.search(r'压力[位价]*[:：]?\s*(\d+\.?\d*)', content)
        resistance = resistance_match.group(1) if resistance_match else "待分析"
        
        # 提取风险提示
        risk_keywords = ["风险", "注意", "谨慎", "回调", "调整"]
        risk_warning = "无明显风险提示"
        for kw in risk_keywords:
            if kw in content:
                # 提取包含风险关键词的句子
                lines = content.split('\n')
                for line in lines:
                    if kw in line:
                        risk_warning = line.strip()
                        break
                break
        
        return DecisionSignal(
            stock_code=stock_code,
            stock_name=stock_name,
            decision=decision,
            confidence=confidence,
            reasoning=content[:1000],  # 限制长度
            risk_warning=risk_warning,
            support_level=support,
            resistance_level=resistance,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _no_api_key_signal(self, stock_code: str, stock_name: str) -> DecisionSignal:
        """生成未配置 API Key 的信号"""
        from datetime import datetime
        
        return DecisionSignal(
            stock_code=stock_code,
            stock_name=stock_name,
            decision="请配置API Key",
            confidence=0.0,
            reasoning="未配置 LLM API Key，无法进行深度分析。\n\n请配置以下环境变量之一：\n- DASHSCOPE_API_KEY（阿里云百炼/通义千问，推荐）\n- DEEPSEEK_API_KEY\n- ARK_API_KEY（豆包）\n\n配置后即可获得 AI 深度推理分析。",
            risk_warning="仅提供技术指标分析，暂无 AI 决策建议",
            support_level="N/A",
            resistance_level="N/A",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _error_signal(self, stock_code: str, stock_name: str, error: str) -> DecisionSignal:
        """生成错误信号"""
        from datetime import datetime
        
        return DecisionSignal(
            stock_code=stock_code,
            stock_name=stock_name,
            decision="分析失败",
            confidence=0.0,
            reasoning=f"API调用失败: {error}",
            risk_warning="请检查网络或API配置",
            support_level="N/A",
            resistance_level="N/A",
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def batch_analyze(self, stocks: List[Dict], thinking_chain: str = TRADER_THINKING_CHAIN) -> List[DecisionSignal]:
        """
        批量分析股票
        
        Args:
            stocks: 股票列表，每个元素包含 code, name, data
            thinking_chain: 思维链提示词
            
        Returns:
            决策信号列表
        """
        signals = []
        
        for stock in stocks:
            signal = self.analyze_stock(
                stock['code'],
                stock['name'],
                stock['data'],
                thinking_chain
            )
            signals.append(signal)
        
        return signals


# 默认使用通义千问（阿里云百炼），免费额度充足
_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取默认 LLM 客户端（使用通义千问）"""
    global _client
    if _client is None:
        # 强制使用通义千问
        _client = LLMClient.create_dashscope()
    return _client


def get_deepseek_client() -> LLMClient:
    """获取 DeepSeek 客户端（兼容旧接口）"""
    return LLMClient.create_deepseek()


def get_dashscope_client() -> LLMClient:
    """获取通义千问客户端"""
    return LLMClient.create_dashscope()


def get_ark_client() -> LLMClient:
    """获取豆包客户端"""
    return LLMClient.create_ark()


# 兼容旧代码
DeepSeekClient = LLMClient


if __name__ == "__main__":
    # 测试代码
    client = DeepSeekClient()
    
    test_data = """
    股票代码: 000001
    股票名称: 上证指数
    
    最新行情:
    收盘价: 3250.50
    涨跌幅: 1.25%
    成交量: 45000000000
    
    成交量异动:
    异动类型: 温和放量
    量比: 1.8
    """
    
    # 注意：需要有效的 API Key 才能测试
    # signal = client.analyze_stock("000001", "上证指数", test_data)
    # print(signal)
    print("请设置 DEEPSEEK_API_KEY 环境变量后测试")
