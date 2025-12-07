import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. 頁面配置
# ==========================================
st.set_page_config(page_title="J Law 戰術掃描器", layout="wide", page_icon="⚔️")

st.title("⚔️ J Law 冠軍操盤室 - 戰術掃描器")
st.markdown("""
**策略核心 (M.E.T.A.)**：
尋找 **強勁趨勢** 中，回調至 **10MA/20MA** 且 **量縮** 的機會。
*(贏大輸小，等待多重優勢共振)*
""")

# ==========================================
# 2. 核心分析函數 (J Law Logic)
# ==========================================
def analyze_jlaw_setup(ticker_symbol):
    try:
        # 下載數據 (取過去 1 年數據以計算均線)
        df = yf.download(ticker_symbol, period="1y", progress=False)
        
        if df.empty or len(df) < 200:
            return None

        # 處理數據 (最新的在最後)
        close = df['Close'].iloc[-1]
        volume = df['Volume'].iloc[-1]
        
        # 計算移動平均線 (MA)
        ma10 = df['Close'].rolling(window=10).mean().iloc[-1]
        ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
        ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
        ma200 = df['Close'].rolling(window=200).mean().iloc[-1]
        
        # 計算平均成交量 (50日)
        avg_vol_50 = df['Volume'].rolling(window=50).mean().iloc[-1]
        vol_ratio = volume / avg_vol_50  # 今日量 / 均量

        # --- J Law 篩選邏輯 ---
        
        # 1. 大趨勢必須向上 (Stage 2)
        trend_condition = close > ma200 and ma50 > ma200
        
        # 2. 強勢特徵 (必須在中短期均線之上或附近)
        # 我們尋找的是回調 (Pullback)，所以價格要在 MA10 或 MA20 附近
        dist_to_ma10 = abs(close - ma10) / close
        dist_to_ma20 = abs(close - ma20) / close
        
        # 定義 "附近" 為差距 2% 以內，且沒有跌破太多
        near_support = (dist_to_ma10 < 0.025) or (dist_to_ma20 < 0.025)
        
        # 3. 量縮 (Volume Dry Up) - 這是 J Law 強調的重點
        # 這是回調買點的關鍵，量縮代表賣壓竭盡
        volume_dry_up = vol_ratio < 0.85  # 今日量小於均量的 85%
        
        setup_type = None
        
        if trend_condition and near_support and volume_dry_up:
            if close > ma10:
                setup_type = "🔥 10MA 超強勢整理 (量縮)"
            elif close > ma20:
                setup_type = "🟡 20MA 標準回調 (網球行為)"
                
        if setup_type:
            return {
                "Ticker": ticker_symbol,
                "Price": close,
                "Setup": setup_type,
                "Vol_Ratio": vol_ratio,
                "MA10": ma10,
                "MA20": ma20,
                "MA50": ma50,
                "DataFrame": df
            }
            
    except Exception as e:
        return None
    return None

# ==========================================
# 3. 側邊欄輸入
# ==========================================
st.sidebar.header("🔍 掃描設定")
default_tickers = "NVDA, TSLA, AMD, AAPL, MSFT, META, GOOGL, AMZN, NFLX, PLTR, COIN, MSTR, SMCI, ARM"
user_input = st.sidebar.text_area("輸入股票代碼 (逗號分隔)", default_tickers, height=150)

run_scan = st.sidebar.button("開始掃描 (Find Edge)", type="primary")

# ==========================================
# 4. 主畫面邏輯
# ==========================================
if run_scan:
    tickers = [t.strip().upper() for t in user_input.split(',')]
    results = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(tickers):
        status_text.text(f"正在分析市場結構: {ticker} ...")
        progress_bar.progress((i + 1) / len(tickers))
        
        res = analyze_jlaw_setup(ticker)
        if res:
            results.append(res)
            
    progress_bar.empty()
    status_text.empty()
    
    if not results:
        st.warning("⚠️ 目前沒有發現符合 J Law 嚴格標準 (趨勢+回調+量縮) 的股票。")
    else:
        st.success(f"✅ 發現 {len(results)} 個潛在 M.E.T.A. 機會！")
        
        for item in results:
            with st.expander(f"{item['Ticker']} - {item['Setup']}", expanded=True):
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.metric("現價", f"${item['Price']:.2f}")
                    st.metric("成交量比 (1.0=均量)", f"{item['Vol_Ratio']:.2f}", delta="量縮" if item['Vol_Ratio'] < 1 else "放量", delta_color="inverse")
                    st.markdown("---")
                    st.write("**關鍵價位:**")
                    st.write(f"10 MA: ${item['MA10']:.2f}")
                    st.write(f"20 MA: ${item['MA20']:.2f}")
                    st.caption("策略：等待突破今日高點進場，止損設在今日低點下方。")

                with col2:
                    # 繪製 K 線圖
                    df_chart = item['DataFrame'].tail(100) # 只看最近 100 天
                    
                    fig = go.Figure(data=[go.Candlestick(x=df_chart.index,
                                    open=df_chart['Open'],
                                    high=df_chart['High'],
                                    low=df_chart['Low'],
                                    close=df_chart['Close'],
                                    name='Price')])
                    
                    # 疊加均線
                    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Close'].rolling(10).mean(), line=dict(color='orange', width=1.5), name='10 MA'))
                    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Close'].rolling(20).mean(), line=dict(color='purple', width=1.5), name='20 MA'))
                    fig.add_trace(go.Scatter(x=df_chart.index, y=df_chart['Close'].rolling(50).mean(), line=dict(color='blue', width=1), name='50 MA'))

                    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(l=0, r=0, t=0, b=0))
                    st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 5. 教學區 (J Law 筆記)
# ==========================================
with st.expander("📚 J Law 投資重點筆記 (Cheatsheet)"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 1. 什麼是 M.E.T.A.?")
        st.write("Multiple Edge Trading Area (多重優勢交易區間)。我們不單靠一條線交易，我們要靠多個理由重疊在同一個位置。")
        st.write("- **趨勢**: 向上")
        st.write("- **位置**: 支持位/均線")
        st.write("- **動能**: 量縮回調")
    with c2:
        st.markdown("### 2. 交易執行")
        st.write("- **進場**: 不要掛單在支撐接刀！要等待價格**突破前一日高點**才進場 (這叫 Follow Through)。")
        st.write("- **止損**: 跌破支撐區間/K線低點就走，不要留戀。")
        st.write("- **目標**: 賺賠比至少 3:1。")
