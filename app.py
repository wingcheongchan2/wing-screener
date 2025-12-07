import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ==========================================
# 1. 系統設置
# ==========================================
st.set_page_config(page_title="J Law 狙擊手操盤室", layout="wide", page_icon="🎯")

# CSS 美化
st.markdown("""
<style>
    .metric-card {border: 1px solid #e6e6e6; padding: 15px; border-radius: 5px; margin-bottom: 10px;}
    .stProgress .st-bo {background-color: #f63366;}
</style>
""", unsafe_allow_html=True)

st.title("🎯 J Law 狙擊手操盤室：全方位戰術系統")
st.markdown("""
**核心指令**：此系統將自動掃描市場，尋找 **M.E.T.A. (多重優勢)** 進場點。
**圖表功能**：自動標示 **Entry (買入)**、**Stop (止損)**、**Target (目標)** 及 **MA Support (支撐)**。
""")

# ==========================================
# 2. 獲取 S&P 500 完整名單
# ==========================================
@st.cache_data
def get_sp500_tickers():
    # 這裡透過維基百科爬取最新的 S&P 500 成分股，確保名單夠多
    try:
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        tickers = df['Symbol'].tolist()
        # 修正一些代碼格式 (例如 BRK.B -> BRK-B)
        tickers = [t.replace('.', '-') for t in tickers]
        return tickers
    except:
        # 如果爬蟲失敗，返回一個較大的預設清單
        return ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "NFLX", "PLTR", "COIN", "MSTR", "SMCI", "ARM", "AVGO", "COST", "PEP", "CSCO", "TMUS", "QCOM", "TXN", "INTU", "INTC", "AMAT", "BKNG", "SBUX", "MDLZ", "ADP", "GILD", "LRCX", "ADI", "VRTX", "REGN", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR", "CSX", "MAR", "PYPL", "ASML", "MNST", "ORLY", "ODFL", "LULU", "UBER", "ABNB", "DASH", "NET", "DDOG", "ZS", "CRWD", "TTD", "APP"]

# ==========================================
# 3. 核心分析引擎 (J Law 邏輯)
# ==========================================
def analyze_stock(ticker, df):
    try:
        if len(df) < 200: return None
        
        # 提取數據
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        close = curr['Close']
        high = curr['High']
        low = curr['Low']
        volume = curr['Volume']
        
        # 計算均線
        sma10 = df['Close'].rolling(10).mean().iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 計算均量
        avg_vol = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = volume / avg_vol
        
        # --- J Law 策略條件 ---
        
        # 1. 趨勢過濾：長期上升趨勢
        if not (close > sma200 and sma50 > sma200):
            return None
            
        setup_type = None
        support_val = 0
        
        # 2. 回調支撐：尋找價格回落到 10MA 或 20MA
        # 計算最低價與均線的距離
        dist_10 = abs(low - sma10) / sma10
        dist_20 = abs(low - sma20) / sma20
        tolerance = 0.02 # 2% 誤差範圍
        
        if dist_10 <= tolerance and close >= sma10 * 0.98:
            setup_type = "10MA 強力支撐 (Super Strong)"
            support_val = sma10
        elif dist_20 <= tolerance and close >= sma20 * 0.98:
            setup_type = "20MA 網球行為 (Tennis Ball)"
            support_val = sma20
            
        # 3. 量能確認：必須縮量
        if setup_type:
            if vol_ratio < 1.0: # 嚴格縮量 < 0.9, 寬鬆 < 1.0
                
                # 計算交易點位
                entry = high + 0.10 # 突破高點
                stop = low - 0.10   # 跌破低點
                
                # ATR 保護 (防止止損過窄)
                tr = max(high-low, abs(high-prev['Close']), abs(low-prev['Close']))
                if (entry - stop) < tr:
                    stop = entry - tr # 至少 1 ATR 空間
                    
                risk = entry - stop
                target = entry + (risk * 3) # 3R 獲利
                
                return {
                    "Ticker": ticker,
                    "Strategy": setup_type,
                    "Close": close,
                    "Entry": round(entry, 2),
                    "Stop": round(stop, 2),
                    "Target": round(target, 2),
                    "Support": round(support_val, 2),
                    "Vol_Ratio": round(vol_ratio, 2),
                    "Risk": round(risk, 2),
                    "DF": df # 儲存數據以供畫圖
                }
    except:
        return None
    return None

# ==========================================
# 4. 專業繪圖引擎 (Plotly Visualization)
# ==========================================
def plot_jlaw_chart(data_dict):
    df = data_dict['DF'].tail(100) # 只畫最近 100 天
    ticker = data_dict['Ticker']
    
    fig = go.Figure()

    # 1. K線圖
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Price'
    ))

    # 2. 移動平均線 (支撐與趨勢)
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(10).mean(), line=dict(color='#FF9800', width=1.5), name='10 MA (強勢)'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(20).mean(), line=dict(color='#9C27B0', width=1.5), name='20 MA (波段)'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'].rolling(50).mean(), line=dict(color='#2196F3', width=1), name='50 MA (中期)'))

    # 3. 繪製交易計劃線 (Entry, Stop, Target)
    # Entry Line (Blue)
    fig.add_shape(type="line",
        x0=df.index[-5], y0=data_dict['Entry'], x1=df.index[-1] + timedelta(days=5), y1=data_dict['Entry'],
        line=dict(color="Blue", width=2, dash="dash"),
    )
    fig.add_annotation(x=df.index[-1], y=data_dict['Entry'], text=f"Entry: ${data_dict['Entry']}", showarrow=True, arrowhead=1, ax=40, ay=-10, bgcolor="blue", font=dict(color="white"))

    # Stop Loss Line (Red)
    fig.add_shape(type="line",
        x0=df.index[-5], y0=data_dict['Stop'], x1=df.index[-1] + timedelta(days=5), y1=data_dict['Stop'],
        line=dict(color="Red", width=2, dash="dot"),
    )
    fig.add_annotation(x=df.index[-1], y=data_dict['Stop'], text=f"Stop: ${data_dict['Stop']}", showarrow=True, arrowhead=1, ax=40, ay=10, bgcolor="red", font=dict(color="white"))

    # Target Line (Green)
    fig.add_shape(type="line",
        x0=df.index[-5], y0=data_dict['Target'], x1=df.index[-1] + timedelta(days=5), y1=data_dict['Target'],
        line=dict(color="Green", width=2, dash="dash"),
    )
    fig.add_annotation(x=df.index[-1], y=data_dict['Target'], text=f"Target (3R): ${data_dict['Target']}", showarrow=True, arrowhead=1, ax=40, ay=-10, bgcolor="green", font=dict(color="white"))

    # 4. 圖表設定
    fig.update_layout(
        title=f"{ticker} 交易戰術圖 - {data_dict['Strategy']}",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=600,
        template="plotly_white",
        margin=dict(l=50, r=50, t=50, b=50)
    )

    return fig

# ==========================================
# 5. 主程序與 UI
# ==========================================

# 側邊欄：搜尋設定
st.sidebar.header("🔍 戰術搜尋設定")
mode = st.sidebar.radio("搜尋模式", ["S&P 500 全掃描 (慢)", "Nasdaq 100 掃描 (快)", "自定義輸入"])

custom_tickers = ""
if mode == "自定義輸入":
    st.sidebar.info("請輸入你在 TradingView 看到的股票代碼，用逗號分隔。")
    custom_tickers = st.sidebar.text_area("股票代碼 (例: NVDA, COIN, AI)", "NVDA, TSLA, AMD, PLTR")

if st.sidebar.button("🚀 啟動狙擊手掃描", type="primary"):
    
    # 1. 決定股票清單
    ticker_list = []
    if mode == "S&P 500 全掃描 (慢)":
        with st.spinner("正在獲取 S&P 500 最新成分股..."):
            ticker_list = get_sp500_tickers()
    elif mode == "Nasdaq 100 掃描 (快)":
        ticker_list = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "AMD", "NFLX", "PEP", "CSCO", "TMUS", "QCOM", "TXN", "INTU", "INTC", "AMAT", "BKNG", "SBUX", "MDLZ", "ADP", "GILD", "LRCX", "ADI", "VRTX", "REGN", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR", "CSX", "MAR", "PYPL", "ASML", "MNST", "ORLY", "ODFL", "LULU", "UBER", "ABNB", "DASH", "NET", "DDOG", "ZS", "CRWD", "TTD", "APP"]
    else:
        if custom_tickers:
            ticker_list = [x.strip().upper() for x in custom_tickers.split(',')]
        else:
            st.error("請輸入股票代碼！")
            st.stop()

    st.write(f"正在掃描 {len(ticker_list)} 隻股票... 請耐心等待戰術運算。")
    
    # 2. 批量下載數據 (使用 threads 加速)
    try:
        raw_data = yf.download(ticker_list, period="1y", group_by='ticker', threads=True, progress=False)
        
        valid_results = []
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(ticker_list):
            progress_bar.progress((i + 1) / len(ticker_list))
            
            try:
                # 處理單一股票與多股票的數據結構差異
                if len(ticker_list) == 1:
                    df_stock = raw_data
                else:
                    df_stock = raw_data[ticker].dropna()
                
                if not df_stock.empty:
                    result = analyze_stock(ticker, df_stock)
                    if result:
                        valid_results.append(result)
            except:
                continue
                
        progress_bar.empty()

        # 3. 顯示結果
        if valid_results:
            st.success(f"🎯 任務完成！發現 {len(valid_results)} 個潛在交易機會。")
            
            # 分頁顯示每個機會
            tabs = st.tabs([f"{res['Ticker']}" for res in valid_results])
            
            for i, tab in enumerate(tabs):
                res = valid_results[i]
                with tab:
                    # 頂部數據列
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("策略", res['Strategy'])
                    c2.metric("最新收盤", f"${res['Close']}")
                    c3.metric("成交量比 (Dry Up)", f"{int(res['Vol_Ratio']*100)}%")
                    c4.metric("風險回報", "1 : 3")
                    
                    # 互動圖表
                    fig = plot_jlaw_chart(res)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 交易計劃詳情
                    with st.container():
                        st.markdown("### 📝 交易執行計劃 (Execution Plan)")
                        col_buy, col_stop, col_target = st.columns(3)
                        
                        col_buy.info(f"""
                        **🔵 買入點 (Entry): ${res['Entry']}**
                        *邏輯*：突破昨日高點確認 (Confirmation)。
                        *條件*：必須等待股價升破此價位才進場，不要掛單接刀。
                        """)
                        
                        col_stop.error(f"""
                        **🔴 止損點 (Stop): ${res['Stop']}**
                        *邏輯*：跌破昨日低點或 ATR 保護。
                        *風險*：每股風險 ${res['Risk']}。請根據風險計算倉位大小。
                        """)
                        
                        col_target.success(f"""
                        **🟢 獲利目標 (Target): ${res['Target']}**
                        *邏輯*：3倍風險回報 (3R)。
                        *建議*：到達此價位可減倉或推高止損 (Trailing Stop)。
                        """)
                        
        else:
            st.warning("⚠️ 掃描完成，未發現符合 J Law 嚴格標準的股票。建議觀望或手動輸入其他強勢股代碼。")

    except Exception as e:
        st.error(f"發生錯誤: {str(e)}")

else:
    st.info("👈 請在左側選擇掃描模式並點擊「啟動狙擊手掃描」")
