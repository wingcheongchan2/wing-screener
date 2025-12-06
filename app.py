import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
from io import StringIO
from tradingview_ta import TA_Handler, Interval, Exchange

# ==========================================
# 1. 網站基本設定
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室", layout="wide", page_icon="🚀")

st.title("🚀 J Law (Mark Minervini) 冠軍操盤室")
st.markdown("""
此系統結合 **Trend Template (趨勢樣板)** 與 **Pullback (拉回買入)** 策略。
*   **冠軍模式**：尋找正在創新高、動能最強的股票。
*   **拉回模式**：尋找強勢股回調至 **10天線** 或 **20天線** 的低風險買點。
""")

# 初始化 Session State
if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 獲取股票名單 (防彈版)
# ==========================================
@st.cache_data
def get_nasdaq100():
    # 嘗試 1: Wikipedia
    headers = {'User-Agent': 'Mozilla/5.0'}
    tickers = []
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'
        response = requests.get(url, headers=headers, timeout=5)
        tables = pd.read_html(StringIO(response.text))
        for table in tables:
            if 'Ticker' in table.columns:
                tickers = table['Ticker'].tolist()
                break
    except:
        pass
    
    # 嘗試 2: 後備名單
    if not tickers:
        st.toast("⚠️ 正在使用後備名單掃描...", icon="ℹ️")
        tickers = [
            "NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "COST", "AMD",
            "NFLX", "INTC", "QCOM", "TXN", "HON", "AMGN", "SBUX", "GILD", "ADP", "BKNG",
            "MDLZ", "ISRG", "REGN", "VRTX", "LRCX", "MU", "CSX", "PANW", "KLAC", "SNPS",
            "CRWD", "NET", "DDOG", "ZS", "MSTR", "COIN", "PLTR", "ARM", "SMCI"
        ]
    
    return [t.replace('.', '-') for t in tickers]

# ==========================================
# 3. 顯示 TradingView 圖表 (含 10/20/50/200 MA)
# ==========================================
def show_tv_widget(symbol):
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": 600,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "studies": [
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 10 }}, "title": "10 MA (短期動力)" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA (拉回支撐)" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA (中期)" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 200 }}, "title": "200 MA (長期)" }}
        ]
      }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=600)

# ==========================================
# 4. 核心掃描邏輯 (新增拉回算法)
# ==========================================
def scan_market(tickers, mode):
    results = []
    progress_bar = st.progress(0)
    status = st.empty()
    total = len(tickers)
    
    for i, ticker in enumerate(tickers):
        progress_bar.progress((i + 1) / total)
        status.text(f"分析中: {ticker} ...")
        
        try:
            handler = TA_Handler(
                symbol=ticker,
                screener="america",
                exchange="", 
                interval=Interval.INTERVAL_1_DAY
            )
            analysis = handler.get_analysis()
            
            if analysis:
                close = analysis.indicators.get('close')
                rsi = analysis.indicators.get('RSI')
                sma10 = analysis.indicators.get('SMA10')
                sma20 = analysis.indicators.get('SMA20')
                sma50 = analysis.indicators.get('SMA50')
                sma200 = analysis.indicators.get('SMA200')
                
                if not (close and sma10 and sma20 and sma50 and sma200):
                    continue

                # --- 基礎趨勢過濾 (所有策略都要符合) ---
                # 股價必須高於 200天線，且 50天線 > 200天線 (多頭排列)
                trend_ok = (close > sma200) and (sma50 > sma200)
                
                if not trend_ok:
                    continue

                is_match = False
                note = ""

                # === 策略 1: 嚴格 J Law (突破/強勢) ===
                if mode == "嚴格 J Law (冠軍突破)":
                    # 股價強勢，位於所有均線之上，且 RSI 強勁
                    if (close > sma10) and (close > sma50) and (rsi > 60):
                        is_match = True
                        note = "🔥 強勢突破中"

                # === 策略 2: 拉回買入 (Pullback) ===
                elif mode == "J Law 拉回買入 (Pullback)":
                    # 股價必須在 50天線之上 (確保不是暴跌)
                    if close > sma50:
                        # 檢查是否回調到 10MA 附近 (誤差 2.5% 內)
                        diff_10 = abs(close - sma10) / close
                        # 檢查是否回調到 20MA 附近 (誤差 2.5% 內)
                        diff_20 = abs(close - sma20) / close
                        
                        if diff_10 < 0.025:
                            is_match = True
                            note = "🟢 回調至 10MA (超強勢)"
                        elif diff_20 < 0.025:
                            is_match = True
                            note = "🟡 回調至 20MA (正常)"

                # === 策略 3: 寬鬆模式 ===
                elif mode == "寬鬆模式 (觀察用)":
                    if close > sma200:
                        is_match = True
                        note = "✅ 趨勢向上"

                if is_match:
                    results.append({
                        "代號": ticker,
                        "現價": round(close, 2),
                        "RSI": round(rsi, 2),
                        "信號": note,
                        "10 MA": round(sma10, 2),
                        "20 MA": round(sma20, 2)
                    })
                    
        except:
            continue
            
    progress_bar.empty()
    status.empty()
    return results

# ==========================================
# 5. 介面操作
# ==========================================

st.sidebar.header("⚙️ 掃描策略")
scan_mode = st.sidebar.radio(
    "請選擇策略：", 
    ["J Law 拉回買入 (Pullback)", "嚴格 J Law (冠軍突破)", "寬鬆模式 (觀察用)"]
)

st.sidebar.info("""
**策略說明：**
*   **拉回買入**：適合想「低吸」的交易者。尋找回調至 10/20MA 的股票。
*   **冠軍突破**：適合想「追強」的交易者。尋找 RSI 強勁且創新高的股票。
""")

if st.sidebar.button("🔍 開始掃描", type="primary"):
    with st.spinner(f"正在執行：{scan_mode}..."):
        stock_list = get_nasdaq100()
    
    if stock_list:
        results = scan_market(stock_list, scan_mode)
        if results:
            df = pd.DataFrame(results)
            # 將符合條件的股票存入 Session State
            st.session_state['scan_results'] = df
        else:
            st.warning("⚠️ 沒有股票符合當前條件。嘗試切換策略或等待市況好轉。")
            st.session_state['scan_results'] = None

# --- 顯示結果 ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader(f"📋 掃描結果: {scan_mode}")
    
    if st.session_state['scan_results'] is not None:
        df_res = st.session_state['scan_results']
        
        # 顯示數量
        st.write(f"共找到 {len(df_res)} 隻股票")
        
        # 顯示表格 (Highlight RSI)
        st.dataframe(
            df_res.style.background_gradient(subset=['RSI'], cmap='Greens'),
            use_container_width=True,
            hide_index=True
        )
        
        st.divider()
        st.write("👇 **點擊下方選擇股票看圖：**")
        selected_ticker = st.selectbox("股票代號", df_res['代號'].tolist())

    else:
        st.info("👈 請在左側點擊按鈕開始。")
        selected_ticker = None

with col2:
    st.subheader("📈 J Law 技術分析圖")
    if selected_ticker:
        # 獲取選中股票的詳細信息
        row = df_res[df_res['代號'] == selected_ticker].iloc[0]
        
        # 顯示信號提示
        if "拉回" in row['信號']:
            st.success(f"🎯 **交易機會：{row['信號']}**")
            st.caption("建議觀察：股價是否在均線處出現「止跌回升」的K線形態（如錘頭線、長下影線）。")
        elif "突破" in row['信號']:
            st.warning(f"🔥 **交易機會：{row['信號']}**")
            st.caption("建議觀察：成交量是否配合放大？")
            
        show_tv_widget(selected_ticker)
    else:
        st.write("等待掃描結果...")
