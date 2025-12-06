import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import streamlit.components.v1 as components
from io import StringIO

# ==========================================
# 1. 系統設置
# ==========================================
st.set_page_config(page_title="J Law 冠軍操盤室 (戰術版)", layout="wide", page_icon="⚔️")

st.title("⚔️ J Law 冠軍操盤室：智能戰術執行板")
st.markdown("""
**核心功能**：不僅幫你選股，更提供完整的 **J Law 拉回買入 (Pullback) 交易劇本**。
**重點指標**：支撐測試 (10/20MA) + 縮量 (Volume Dry Up) + 突破確認 (Confirmation)。
""")

if 'scan_results' not in st.session_state:
    st.session_state['scan_results'] = None

# ==========================================
# 2. 數據獲取
# ==========================================
@st.cache_data
def get_nasdaq100_tickers():
    return [
        "NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
        "AMD", "NFLX", "PEP", "LIN", "ADBE", "CSCO", "TMUS", "QCOM", "TXN", "INTU",
        "AMGN", "INTC", "ISRG", "HON", "AMAT", "BKNG", "SBUX", "MDLZ", "GILD", "ADP",
        "VRTX", "LRCX", "REGN", "ADI", "PANW", "MU", "SNPS", "KLAC", "CDNS", "CHTR",
        "CSX", "MAR", "PYPL", "ASML", "ORLY", "MNST", "NXPI", "ROP", "LULU", "AEP",
        "ADSK", "PDD", "WDAY", "FTNT", "KDP", "PAYX", "CTAS", "PCAR", "MCHP", "ODFL",
        "CRWD", "NET", "DDOG", "ZS", "MSTR", "COIN", "PLTR", "ARM", "SMCI", "UBER"
    ]

# ==========================================
# 3. 核心運算引擎 (深度分析邏輯)
# ==========================================
def analyze_stock_deep(ticker, df):
    try:
        # 提取數據
        close = df['Close'].iloc[-1]
        prev_close = df['Close'].iloc[-2]
        high = df['High'].iloc[-1]
        low = df['Low'].iloc[-1]
        vol = df['Volume'].iloc[-1]
        
        # 計算均線
        sma10 = df['Close'].rolling(10).mean().iloc[-1]
        sma20 = df['Close'].rolling(20).mean().iloc[-1]
        sma50 = df['Close'].rolling(50).mean().iloc[-1]
        sma200 = df['Close'].rolling(200).mean().iloc[-1]
        
        # 計算平均成交量 (50日)
        avg_vol_50 = df['Volume'].rolling(50).mean().iloc[-1]
        vol_ratio = vol / avg_vol_50 # 量能比
        
        # 計算 RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # --- 策略邏輯判斷 ---
        setup_found = False
        reasons = [] # 儲存買入原因
        setup_name = ""
        support_level = 0
        
        # 1. 大趨勢過濾
        if close > sma200 and sma50 > sma200:
            
            # --- 拉回策略 ---
            # 必須在中期上升趨勢中 (股價 > 50MA)
            if close > sma50:
                
                # 檢查 10MA (誤差 1.5%)
                dist_10 = abs(low - sma10) / sma10
                # 檢查 20MA (誤差 1.5%)
                dist_20 = abs(low - sma20) / sma20
                
                if dist_10 <= 0.015:
                    setup_found = True
                    setup_name = "🟢 10MA 強力支撐 (Super Strength)"
                    support_level = sma10
                    reasons.append("股價回調至 10天移動平均線，顯示極強勢的買盤支撐。")
                
                elif dist_20 <= 0.015:
                    setup_found = True
                    setup_name = "🟡 20MA 標準拉回 (Tennis Ball Action)"
                    support_level = sma20
                    reasons.append("股價回調至 20天移動平均線，這是最經典的波段買點。")
            
            # --- 冠軍突破策略 ---
            elif rsi > 65 and close > sma10:
                 setup_found = True
                 setup_name = "🔥 動能突破 (High Momentum)"
                 support_level = sma10
                 reasons.append("RSI 強勢 (>65)，股價站穩短期均線，準備發動攻勢。")

            # --- 量能分析 (J Law 重點) ---
            if setup_found:
                if vol_ratio < 0.8:
                    reasons.append(f"✅ **縮量回調 (Volume Dry Up)**：今日成交量僅為平均的 {int(vol_ratio*100)}%。這代表賣壓已經枯竭，大戶沒有出貨。")
                elif vol_ratio > 1.2:
                    reasons.append(f"⚠️ **放量注意**：今日成交量較大 ({int(vol_ratio*100)}%)，請確認收盤是否收在均線之上（有承接）。")
                else:
                    reasons.append("量能正常。")

                # 計算交易參數
                buy_trigger = high + 0.05 # 突破今日高點
                stop_loss = low - 0.05    # 跌破今日低點
                risk = buy_trigger - stop_loss
                target = buy_trigger + (risk * 3) # 3R 目標
                
                return {
                    "代號": ticker,
                    "現價": round(close, 2),
                    "策略": setup_name,
                    "RSI": round(rsi, 1),
                    "買入原因": reasons,
                    "買入觸發": round(buy_trigger, 2),
                    "止損": round(stop_loss, 2),
                    "目標": round(target, 2),
                    "風險": round((risk / buy_trigger) * 100, 2)
                }
                
    except:
        return None
    return None

# ==========================================
# 4. 顯示詳細戰術板 (UI 核心)
# ==========================================
def show_tactical_board(data):
    st.markdown("---")
    
    # 標題區
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader(f"📊 {data['代號']} 交易戰術分析")
        st.caption(f"策略模式：{data['策略']} | RSI: {data['RSI']}")
    with c2:
        # 風險提示
        if data['風險'] < 5:
            st.success(f"風險度：{data['風險']}% (低風險 ✅)")
        else:
            st.warning(f"風險度：{data['風險']}% (中等，注意倉位)")

    # 內容區
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("#### 🧐 為什麼選這隻？ (Why)")
        for reason in data['買入原因']:
            st.write(f"- {reason}")
            
        st.info("""
        **💡 J Law 心法：**
        我們不在股價下跌時買入，我們等待「網球行為」(Tennis Ball Action)。
        當股價碰到均線像網球一樣反彈，並且**成交量縮小**，就是機會。
        """)

    with col_right:
        st.markdown("#### 🛠️ 如何執行交易？ (How)")
        st.markdown(f"""
        1.  **設定警報 (Alert)**：在股價 **${data['買入觸發']}** 設定到價提示。
        2.  **買入時機**：當股價**升破** ${data['買入觸發']} (昨日高點) 時進場。這代表調整結束，多頭回歸。
        3.  **設定止損**：買入後立刻設定止損單在 **${data['止損']}** (昨日低點下方)。
        4.  **獲利目標**：第一目標看 **${data['目標']}** (3倍風險回報)。
        """)
    
    # 關鍵數據橫幅
    st.markdown("### 🔑 關鍵價位 Key Levels")
    k1, k2, k3 = st.columns(3)
    k1.metric("🟢 買入觸發 (Trigger)", f"${data['買入觸發']}")
    k2.metric("🔴 止損防守 (Stop)", f"${data['止損']}")
    k3.metric("🎯 獲利目標 (Target)", f"${data['目標']}")

    # TradingView Widget
    html_code = f"""
    <div class="tradingview-widget-container">
      <div id="tradingview_chart"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget(
      {{
        "width": "100%",
        "height": 500,
        "symbol": "{data['代號']}",
        "interval": "D",
        "timezone": "Exchange",
        "theme": "dark",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "hide_side_toolbar": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart",
        "studies": [
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 10 }}, "title": "10 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 20 }}, "title": "20 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 50 }}, "title": "50 MA" }},
          {{ "id": "MASimple@tv-basicstudies", "inputs": {{ "length": 200 }}, "title": "200 MA" }}
        ]
      }}
      );
      </script>
    </div>
    """
    components.html(html_code, height=500)

# ==========================================
# 5. 主程序邏輯
# ==========================================

# 側邊欄
st.sidebar.header("🔍 掃描設定")
source = st.sidebar.radio("股票池", ["Nasdaq 100", "自定義 (ARK/NVDA/SMCI...)"])
custom_input = ""
if source == "自定義 (ARK/NVDA/SMCI...)":
    custom_input = st.sidebar.text_area("輸入代號 (逗號分隔)", "PLTR, COIN, SMCI, ARM, MSTR, HOOD, DKNG")

if st.sidebar.button("🚀 執行戰術掃描", type="primary"):
    target_list = []
    if source == "Nasdaq 100":
        target_list = get_nasdaq100_tickers()
    else:
        if custom_input:
            target_list = [x.strip().upper() for x in custom_input.split(',')]
        else:
            st.error("請輸入股票代號")
            
    if target_list:
        with st.spinner("正在分析市場結構與量價關係..."):
            # 下載數據
            data = yf.download(target_list, period="1y", group_by='ticker', progress=False)
            
            results = []
            progress = st.progress(0)
            
            for i, ticker in enumerate(target_list):
                progress.progress((i + 1) / len(target_list))
                try:
                    if len(target_list) == 1:
                        df = data
                    else:
                        df = data[ticker]
                    
                    df = df.dropna()
                    if not df.empty and len(df) > 200:
                        res = analyze_stock_deep(ticker, df)
                        if res:
                            results.append(res)
                except:
                    continue
            
            progress.empty()
            
            if results:
                st.session_state['scan_results'] = pd.DataFrame(results)
            else:
                st.warning("沒有發現符合 J Law 嚴格標準的股票。")
                st.session_state['scan_results'] = None

# 顯示結果
if st.session_state['scan_results'] is not None:
    df = st.session_state['scan_results']
    
    # 選擇股票
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📋 符合清單")
        st.write(f"共 {len(df)} 隻")
        st.dataframe(df[['代號', '策略', 'RSI']], use_container_width=True, hide_index=True)
        target = st.selectbox("👇 點擊查看戰術詳情：", df['代號'].tolist())
    
    with c2:
        if target:
            # 獲取該行數據轉為字典
            row_dict = df[df['代號'] == target].to_dict('records')[0]
            show_tactical_board(row_dict)
else:
    st.info("👈 請在左側開始掃描")
