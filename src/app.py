"""
AlphaLens Pro V9.0 - Streamlit 主应用
AI 驱动的股票深度推理分析系统

特性：
- 通义千问大模型深度推理
- Akshare 实时数据
- 思维链分析
- 全面屏沉浸式 UI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os

from alphalens.analyzer import IndustryAnalyzer
from alphalens.data_fetcher import IndustryDataFetcher


# ==================== V9.0 极致优化：自定义 CSS ====================
def apply_custom_css():
    """应用自定义 CSS 实现全面屏沉浸式体验"""
    
    st.markdown("""
    <style>
    /* 全面屏适配 - 去除左右留白 */
    .main .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* 隐藏右上角菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 移除默认的 padding */
    .main {
        padding: 0;
    }
    
    /* 输入框样式 - 固定底部 */
    .stTextInput > div > div {
        background-color: #0e1117;
        border: 1px solid #262730;
        border-radius: 8px;
    }
    
    /* 仪表盘卡片样式 */
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid #2d4a6f;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .metric-card-buy {
        background: linear-gradient(135deg, #0d4f2f 0%, #062918 100%);
        border: 1px solid #0f7a4a;
    }
    
    .metric-card-sell {
        background: linear-gradient(135deg, #4f1e1e 0%, #2b0d0d 100%);
        border: 1px solid #7a1f1f;
    }
    
    .metric-card-hold {
        background: linear-gradient(135deg, #3d3d1e 0%, #1e1e0d 100%);
        border: 1px solid #6a6a1f;
    }
    
    /* 标题样式 */
    .stock-title {
        font-size: 2rem;
        font-weight: bold;
        color: #00d4ff;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
    }
    
    /* 决策信号样式 */
    .decision-signal {
        font-size: 1.8rem;
        font-weight: bold;
        text-align: center;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .signal-buy {
        background: linear-gradient(90deg, #00c853, #69f0ae);
        color: #000;
    }
    
    .signal-sell {
        background: linear-gradient(90deg, #ff5252, #ff8a80);
        color: #fff;
    }
    
    .signal-hold {
        background: linear-gradient(90deg, #ffd740, #ffab40);
        color: #000;
    }
    
    /* 支撑位压力位仪表盘 */
    .level-card {
        display: inline-block;
        padding: 15px 25px;
        margin: 5px;
        border-radius: 8px;
        text-align: center;
    }
    
    .support-card {
        background: #1b5e20;
        border: 2px solid #4caf50;
    }
    
    .resistance-card {
        background: #b71c1c;
        border: 2px solid #f44336;
    }
    
    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0e1117;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #262730;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4a4a5a;
    }
    
    /* K线图容器 */
    .chart-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    
    /* 风险提示 */
    .risk-warning {
        background: linear-gradient(90deg, #ff6f00, #ff8f00);
        color: #000;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
    }
    
    /* 置信度进度条 */
    .confidence-bar {
        height: 10px;
        border-radius: 5px;
        background: #262730;
        overflow: hidden;
    }
    
    .confidence-fill {
        height: 100%;
        border-radius: 5px;
        transition: width 0.5s ease;
    }
    </style>
    """, unsafe_allow_html=True)


# ==================== 行业分析渲染函数 ====================

def render_industry_chart(daily_df: pd.DataFrame, industry_name: str):
    """
    渲染行业走势图表
    """
    if daily_df.empty:
        st.warning("暂无走势数据")
        return
    
    # 转换日期
    if '日期' in daily_df.columns:
        daily_df['日期'] = pd.to_datetime(daily_df['日期'])
    
    # 取最近60天
    df = daily_df.tail(60)
    
    # 创建图表
    fig = go.Figure()
    
    # 收盘价走势
    fig.add_trace(go.Scatter(
        x=df['日期'],
        y=df['收盘'],
        mode='lines',
        name='收盘价',
        line=dict(color='#00d4ff', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    
    # 布局
    fig.update_layout(
        title=dict(
            text=f"{industry_name} 近期走势",
            font=dict(size=18, color='#00d4ff')
        ),
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14, 17, 23, 0.5)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_industry_metrics(result: dict):
    """
    渲染行业分析指标
    """
    analysis = result.get('industry_analysis', {})
    signal = result.get('llm_signal')
    etf_df = result.get('etf_list')
    
    if not analysis:
        return
    
    # 核心指标
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        change = analysis.get('avg_change', 0)
        st.metric("行业平均涨跌幅", f"{change:+.2f}%")
    
    with col2:
        stocks = analysis.get('stocks_count', 0)
        st.metric("成分股数量", f"{stocks}只")
    
    with col3:
        up = analysis.get('up_count', 0)
        down = analysis.get('down_count', 0)
        st.metric("上涨/下跌", f"{up}/{down}")
    
    with col4:
        inflow = analysis.get('main_inflow', 0)
        st.metric("主力净流入", f"{inflow/10000:.0f}万")
    
    # 投资建议
    st.markdown("---")
    
    if signal:
        # 信号颜色
        signal_class = "signal-hold"
        if "买入" in signal.decision:
            signal_class = "signal-buy"
        elif "卖出" in signal.decision or "减仓" in signal.decision:
            signal_class = "signal-sell"
        elif "关注" in signal.decision:
            signal_class = "signal-focus"
        
        st.markdown(f"""
        <div class="decision-signal {signal_class}">
            {signal.decision}
        </div>
        """, unsafe_allow_html=True)
        
        # 置信度
        confidence_pct = int(signal.confidence * 100)
        conf_color = "#00c853" if confidence_pct >= 70 else "#ff9800" if confidence_pct >= 50 else "#ff5252"
        
        st.markdown(f"""
        <div style="margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>置信度</span>
                <span style="color: {conf_color}; font-weight: bold;">{confidence_pct}%</span>
            </div>
            <div class="confidence-bar">
                <div class="confidence-fill" style="width: {confidence_pct}%; background: {conf_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ETF推荐
        if etf_df is not None and not etf_df.empty:
            st.subheader("📈 相关ETF基金")
            
            for _, etf in etf_df.head(5).iterrows():
                code = etf.get('代码', '')
                name = etf.get('名称', '')
                price = etf.get('最新价', 0)
                change = etf.get('涨跌幅', 0)
                
                change_color = "#00c853" if change > 0 else "#ff5252"
                
                st.markdown(f"""
                <div class="etf-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-weight: bold; font-size: 1.1rem;">{name}</span>
                            <span style="color: #888; margin-left: 10px;">{code}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="font-size: 1.2rem; font-weight: bold;">{price:.3f}</span>
                            <span style="color: {change_color}; margin-left: 10px;">{change:+.2f}%</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # 推理过程
        with st.expander("📝 查看深度分析", expanded=True):
            st.markdown(signal.reasoning)
        
        # 风险提示
        if signal.risk_warning:
            st.markdown(f"""
            <div class="risk-warning">
                ⚠️ 风险提示: {signal.risk_warning}
            </div>
            """, unsafe_allow_html=True)
    else:
        # 没有AI信号时，显示基础建议
        recommendation = analysis.get('recommendation', '观望')
        st.info(f"📊 基础分析建议: **{recommendation}**")


def render_hot_industries(analyzer: IndustryAnalyzer):
    """
    渲染热门行业板块
    """
    st.subheader("🔥 今日热门行业")
    
    try:
        hot_df = analyzer.get_hot_industries(10)
        
        if not hot_df.empty:
            # 第一行：前5个
            cols1 = st.columns(5)
            for i, (idx, row) in enumerate(hot_df.head(5).iterrows()):
                with cols1[i]:
                    name = row.get('板块名称', '')
                    change = row.get('涨跌幅', 0)
                    change_color = "#00c853" if change > 0 else "#ff5252"
                    bg_color = "#0d3320" if change > 0 else "#331010"
                    border_color = "#00c853" if change > 0 else "#ff5252"
                    
                    # 点击跳转
                    if st.button(f"**{name}**\n{change:+.2f}%", key=f"hot_{name}", use_container_width=True):
                        st.session_state.hot_industry_selected = name
                        st.rerun()
            
            # 第二行：后5个
            cols2 = st.columns(5)
            for i, (idx, row) in enumerate(hot_df.iloc[5:10].iterrows()):
                with cols2[i]:
                    name = row.get('板块名称', '')
                    change = row.get('涨跌幅', 0)
                    change_color = "#00c853" if change > 0 else "#ff5252"
                    
                    if st.button(f"**{name}**\n{change:+.2f}%", key=f"hot_{name}_2", use_container_width=True):
                        st.session_state.hot_industry_selected = name
                        st.rerun()
    except Exception as e:
        st.warning(f"获取热门行业失败: {e}")


def render_ai_recommendations(analyzer: IndustryAnalyzer):
    """
    渲染AI推荐行业
    """
    st.subheader("💎 AI 推荐行业")
    
    # 检查是否已经有缓存的推荐结果
    if "ai_recommendations" not in st.session_state:
        st.session_state.ai_recommendations = None
        st.session_state.ai_recommendations_loading = False
    
    # 显示按钮让用户主动触发AI分析
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🤖 获取AI推荐", type="primary", use_container_width=True, key="ai_rec_btn"):
            st.session_state.ai_recommendations_loading = True
            st.session_state.ai_recommendations = None
            st.rerun()
    
    with col2:
        # 清除缓存按钮
        if st.session_state.ai_recommendations is not None:
            if st.button("🔄 刷新推荐", use_container_width=True, key="refresh_btn"):
                st.session_state.ai_recommendations = None
                st.session_state.ai_recommendations_loading = False
                st.rerun()
    
    # 如果正在加载
    if st.session_state.ai_recommendations_loading:
        st.markdown("### 🤖 AI 推荐分析进展")
        
        # 创建进展状态
        ai_status_text = st.empty()
        ai_progress_bar = st.progress(0)
        ai_detail_text = st.empty()
        
        try:
            # 步骤1: 预加载数据
            ai_status_text.markdown("⏳ **步骤 1/3**: 预加载行业数据...")
            ai_progress_bar.progress(15)
            ai_detail_text.markdown("📥 正在获取行业列表、热门板块、ETF数据...")
            
            # 检查缓存状态
            cache_stats = analyzer.data_fetcher.get_daily_cache_stats()
            if not cache_stats.get('is_fully_loaded'):
                ai_detail_text.markdown("📥 首次加载，正在下载全量数据（约需30-60秒）...")
            else:
                ai_detail_text.markdown("💾 缓存数据已就绪")
            
            ai_progress_bar.progress(30)
            
            # 步骤2: 批量分析行业
            ai_status_text.markdown("🔍 **步骤 2/3**: 批量分析行业数据...")
            ai_progress_bar.progress(50)
            ai_detail_text.markdown("📊 正在分析行业趋势、资金流向、技术指标...")
            
            # 执行AI推荐（带缓存）
            recommendations = analyzer.get_ai_recommendations(use_cache=True)
            
            ai_progress_bar.progress(75)
            
            # 步骤3: AI决策
            ai_status_text.markdown("🧠 **步骤 3/3**: AI 生成投资建议...")
            ai_progress_bar.progress(90)
            ai_detail_text.markdown(f"✅ 已分析完成，筛选出 {len(recommendations)} 个推荐行业")
            
            # 完成
            ai_progress_bar.progress(100)
            ai_status_text.markdown("✅ **AI 分析完成！**")
            ai_detail_text.markdown(f"🎯 发现 {len(recommendations)} 个投资机会")
            
            st.session_state.ai_recommendations = recommendations
            st.session_state.ai_recommendations_loading = False
            
            st.markdown("---")
            
        except Exception as e:
            ai_progress_bar.progress(100)
            ai_status_text.markdown("❌ **AI分析失败**")
            ai_detail_text.markdown(f"错误: {str(e)}")
            st.error(f"AI分析失败: {e}")
            st.session_state.ai_recommendations_loading = False
            return
    
    # 显示推荐结果
    recommendations = st.session_state.ai_recommendations
    
    if recommendations:
        for i, rec in enumerate(recommendations):
            industry = rec.get('industry', '')
            decision = rec.get('decision', '')
            confidence = rec.get('confidence', 0)
            reasoning = rec.get('reasoning', '')
            analysis = rec.get('analysis', {})
            etf_list = rec.get('etf_list')
            
            # 置信度
            conf_pct = int(confidence * 100)
            
            # 行业涨跌幅
            avg_change = analysis.get('avg_change', 0) if analysis else 0
            
            # 决策颜色
            if "买入" in decision or "增持" in decision or "定投" in decision:
                decision_color = "#00c853"
            elif "观望" in decision or "减仓" in decision:
                decision_color = "#ffd740"
            else:
                decision_color = "#2196f3"
            
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #1a2a3a 0%, #0d1520 100%); 
                            border-left: 4px solid {decision_color}; 
                            padding: 15px; border-radius: 8px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.3rem; font-weight: bold; color: #00d4ff;">{industry}</span>
                            <span style="margin-left: 15px; color: {decision_color}; font-weight: bold;">{decision}</span>
                        </div>
                        <div style="text-align: right;">
                            <div style="color: {'#00c853' if avg_change > 0 else '#ff5252'}; font-size: 1.1rem;">{avg_change:+.2f}%</div>
                            <div style="color: #888; font-size: 0.8rem;">置信度 {conf_pct}%</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 推荐理由
                if reasoning:
                    with st.expander("📋 查看推荐理由"):
                        st.markdown(reasoning)
                        
                        # ETF推荐
                        if etf_list is not None and not etf_list.empty:
                            st.markdown("**相关ETF：**")
                            for _, etf in etf_list.head(3).iterrows():
                                etf_name = etf.get('名称', '')
                                etf_price = etf.get('最新价', 0)
                                etf_change = etf.get('涨跌幅', 0)
                                st.markdown(f"- {etf_name}: {etf_price:.3f} ({etf_change:+.2f}%)")
                
                # 一键分析按钮
                if st.button(f"📊 详细分析 →", key=f"rec_{industry}"):
                    st.session_state.pending_analysis = industry
                    st.rerun()
                    
    elif st.session_state.ai_recommendations is None and not st.session_state.ai_recommendations_loading:
        st.info("👆 点击「获取AI推荐」按钮，AI将分析热门行业并推荐投资机会")


def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    计算技术指标
    
    Args:
        df: 日线 DataFrame
        
    Returns:
        添加技术指标后的 DataFrame
    """
    df = df.copy()
    
    # 均线
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    
    # 布林带
    df['MA20_STD'] = df['收盘'].rolling(window=20).std()
    df['BB_UPPER'] = df['MA20'] + 2 * df['MA20_STD']
    df['BB_LOWER'] = df['MA20'] - 2 * df['MA20_STD']
    
    return df


def render_industry_chart(df: pd.DataFrame, industry_name: str):
    """
    渲染行业走势图
    
    Args:
        df: 日线 DataFrame
        industry_name: 行业名称
    """
    if df.empty:
        st.warning("暂无数据")
        return
    
    # 计算技术指标
    df = calculate_technical_indicators(df.tail(90))  # 取最近90天
    
    # 创建 K 线图
    fig = go.Figure()
    
    # K 线
    fig.add_trace(go.Candlestick(
        x=df['日期'],
        open=df['开盘'],
        high=df['最高'],
        low=df['最低'],
        close=df['收盘'],
        name='K线',
        increasing_line_color='#00c853',
        decreasing_line_color='#ff5252'
    ))
    
    # 均线
    fig.add_trace(go.Scatter(x=df['日期'], y=df['MA5'], name='MA5', 
                            line=dict(color='#ffeb3b', width=1)))
    fig.add_trace(go.Scatter(x=df['日期'], y=df['MA10'], name='MA10',
                            line=dict(color='#ff9800', width=1)))
    fig.add_trace(go.Scatter(x=df['日期'], y=df['MA20'], name='MA20',
                            line=dict(color='#2196f3', width=1)))
    
    # 布林带
    fig.add_trace(go.Scatter(x=df['日期'], y=df['BB_UPPER'], name='BB_UPPER',
                            line=dict(color='#9c27b0', width=1), opacity=0.5))
    fig.add_trace(go.Scatter(x=df['日期'], y=df['BB_LOWER'], name='BB_LOWER',
                            line=dict(color='#9c27b0', width=1), opacity=0.5,
                            fill='tonexty', fillcolor='rgba(156, 39, 176, 0.1)'))
    
    # 布局
    fig.update_layout(
        title=dict(
            text=f"{industry_name} 日K线走势",
            font=dict(size=20, color='#00d4ff')
        ),
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        height=600,
        margin=dict(l=50, r=50, t=80, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(14, 17, 23, 0.5)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


# ==================== 主应用 ====================
def main():
    """主函数"""
    st.set_page_config(
        page_title="AlphaLens Pro - 行业基金分析",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # 应用自定义 CSS
    apply_custom_css()
    
    # 标题
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 class="stock-title">AlphaLens Pro</h1>
        <p style="color: #888; font-size: 1rem;">
            🤖 AI 深度推理 | 📊 行业趋势分析 | 🎯 ETF基金投资机会
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 检查 API 配置（支持环境变量和 Streamlit Secrets）
    dashscope_key = os.getenv("DASHSCOPE_API_KEY") or st.secrets.get("DASHSCOPE_API_KEY")
    if not dashscope_key:
        st.warning("⚠️ 未配置通义千问 API Key，AI 分析功能将不可用。请在 Streamlit Cloud 的 Secrets 中添加 DASHSCOPE_API_KEY")
    else:
        st.success("✅ 通义千问 API 已配置")
    
    # 侧边栏：缓存管理
    with st.sidebar:
        st.markdown("### ⚙️ 系统管理")
        
        # 显示缓存状态
        analyzer = IndustryAnalyzer()
        cache_stats = analyzer.data_fetcher.get_daily_cache_stats()
        
        st.markdown("#### 💾 缓存状态")
        st.markdown(f"- 日期: {cache_stats.get('today', 'N/A')}")
        st.markdown(f"- 内存项: {cache_stats.get('memory_items', 0)}")
        st.markdown(f"- 全量加载: {'✅' if cache_stats.get('is_fully_loaded') else '❌'}")
        
        # 强制刷新缓存按钮
        if st.button("🔄 强制刷新缓存", use_container_width=True, type="secondary"):
            with st.spinner("正在清空缓存并重新加载数据..."):
                try:
                    # 清空每日缓存
                    analyzer.data_fetcher.clear_daily_cache()
                    # 重置数据源（尝试回到主数据源）
                    analyzer.data_fetcher.reset_to_primary()
                    st.success("✅ 缓存已清空！下次分析时将重新获取数据。")
                    st.info("💡 提示：页面将自动刷新以应用更改")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 刷新缓存失败: {e}")
        
        # 显示当前数据源状态
        if analyzer.data_fetcher.is_using_backup():
            st.error("⚠️ 当前使用备用数据源（模拟数据）")
            if st.button("🔄 尝试切换回主数据源", use_container_width=True):
                analyzer.data_fetcher.reset_to_primary()
                st.success("✅ 已重置，下次请求将尝试主数据源")
                st.rerun()
        else:
            st.success("✅ 当前使用主数据源（akshare）")
        
        st.markdown("---")
    
    # 行业选择
    
    # 常用行业列表
    common_industries = [
        "半导体", "新能源", "医药生物", "食品饮料", "电子元件",
        "软件服务", "互联网", "通信设备", "银行", "证券",
        "房地产", "建筑工程", "有色金属", "化工行业", "汽车整车",
        "电力行业", "军工", "传媒", "环保", "纺织服装"
    ]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 添加"请选择"选项作为默认值
        options = ["-- 请选择行业 --"] + common_industries
        industry_name = st.selectbox(
            "选择分析行业",
            options=options,
            index=0,
            key="industry_select"
        )
    
    with col2:
        analyze_btn = st.button("🔍 开始分析", type="primary", use_container_width=True)
    
    # 处理待分析行业（来自AI推荐或热门行业点击）
    if st.session_state.get("pending_analysis"):
        industry_name = st.session_state.pending_analysis
        st.session_state.pending_analysis = None
        analyze_btn = True
    
    # 处理热门行业点击
    if st.session_state.get("hot_industry_selected"):
        industry_name = st.session_state.hot_industry_selected
        st.session_state.hot_industry_selected = None
        analyze_btn = True  # 自动触发分析
    
    # 判断是否选择了有效行业
    is_valid_industry = industry_name and industry_name != "-- 请选择行业 --"
    
    # 分析逻辑
    should_analyze = analyze_btn and is_valid_industry
    
    if should_analyze:
        # 创建进展状态容器
        progress_container = st.container()
        
        with progress_container:
            st.markdown("### 📊 分析进展")
            
            # 步骤1: 检查/加载缓存
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            status_text.markdown("⏳ **步骤 1/4**: 检查数据缓存...")
            progress_bar.progress(10)
            
            # 获取缓存统计
            cache_stats = analyzer.data_fetcher.get_daily_cache_stats()
            if not cache_stats.get('is_fully_loaded'):
                status_text.markdown("📥 **步骤 1/4**: 首次加载，正在预加载全量数据...")
                progress_bar.progress(20)
            else:
                status_text.markdown("✅ **步骤 1/4**: 缓存数据已加载")
                progress_bar.progress(25)
            
            # 步骤2: 获取行业数据
            status_text.markdown("📈 **步骤 2/4**: 获取行业行情数据...")
            progress_bar.progress(40)
            
            # 步骤3: 获取成分股数据
            status_text.markdown("🔍 **步骤 3/4**: 获取行业成分股数据...")
            progress_bar.progress(60)
            
            # 步骤4: AI深度分析
            status_text.markdown("🤖 **步骤 4/4**: AI 正在进行深度分析...")
            progress_bar.progress(80)
            
            # 执行分析
            result = analyzer.analyze(industry_name)
            
            # 完成
            progress_bar.progress(100)
            
            # 检查是否使用备用数据源
            is_backup = analyzer.data_fetcher.is_using_backup()
            
            # 显示数据来源
            data_source = result.get('data_source', 'unknown')
            if is_backup:
                source_icon = "⚠️"
                source_text = "演示数据（主数据源不可用）"
            elif data_source == 'cache':
                source_icon = "💾"
                source_text = "缓存数据"
            else:
                source_icon = "🌐"
                source_text = "实时数据"
            
            if result.get("error"):
                status_text.markdown(f"❌ **分析失败**: {result['error']}")
                st.error(f"❌ 分析失败: {result['error']}")
                return
            else:
                status_text.markdown(f"✅ **分析完成** | 数据来源: {source_icon} {source_text}")
                
            # 如果使用备用数据源，显示警告
            if is_backup:
                st.warning("⚠️ 当前使用演示数据（模拟数据）。主数据源暂时不可用，请检查网络连接或稍后重试。")
            
            st.markdown("---")
        
        # 渲染结果
        st.markdown("---")
        
        # 行业标题
        st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <span class="stock-title">{industry_name}</span>
            <span style="color: #888; margin-left: 15px;">行业分析</span>
            <span style="color: #888; margin-left: 15px;">{result.get('llm_signal', {}).timestamp if result.get('llm_signal') else ''}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # 渲染指标
        render_industry_metrics(result)
        
        # 渲染走势图
        if result.get('daily_data') is not None and not result['daily_data'].empty:
            st.markdown("---")
            render_industry_chart(result['daily_data'], industry_name)
    
    # 首页显示热门行业（未选择行业或未点击分析时）
    elif not is_valid_industry or not analyze_btn:
        st.markdown("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <h2>👋 欢迎使用 AlphaLens Pro</h2>
            <p>选择行业或点击下方热门行业，获取 AI 深度分析和 ETF 投资建议</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AI推荐行业
        render_ai_recommendations(analyzer)
        
        st.markdown("---")
        
        # 显示热门行业
        render_hot_industries(analyzer)


if __name__ == "__main__":
    # 初始化 session_state
    if "pending_analysis" not in st.session_state:
        st.session_state.pending_analysis = None
    if "hot_industry_selected" not in st.session_state:
        st.session_state.hot_industry_selected = None
    
    main()
