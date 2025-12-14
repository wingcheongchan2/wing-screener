import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime

# ==========================================
# 0. 系統核心配置 (J Law Ultimate Scanner)
# ==========================================
st.set_page_config(page_title="J Law Alpha: S&P 500 Scanner", layout="wide", page_icon="🔥")

# 檔案設定
PORTFOLIO_FILE = 'alpha_portfolio.csv'
TRADE_LOG_FILE = 'alpha_tradelog.csv'
CAPITAL_PER_TRADE = 10000

# ==========================================
# 1. 專業視覺風格 (Bloomberg Terminal Style)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Oswald:wght@400;700&display=swap');
        
        .stApp { background-color: #000000; color: #cfcfcf; font-family: 'Roboto Mono', monospace; }
        section[data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
        
        /* 評分標籤 */
        .score-box {
            font-size: 28px; font-weight: bold; color: #00E676; border: 2px solid #00E676; 
            padding: 10px; text-align: center; border-radius: 5px; box-shadow: 0 0 15px rgba(0, 230, 118, 0.3);
        }
        
        /* 數據格 */
        .data-grid {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 20px;
        }
        .data-card {
            background: #1e1e1e; padding: 10px; border: 1px solid #444; text-align: center;
        }
        .data-label { font-size: 11px; color: #888; text-transform: uppercase; }
        .data-value { font-size: 18px; color: #fff; font-weight: bold; }
        
        /* 列表樣式 */
        div[data-testid="stRadio"] > label {
            background: #111; border: 1px solid #333; margin-bottom: 5px; padding: 10px; color: #eee;
        }
        div[data-testid="stRadio"] > label:hover { border-color: #00E676; color: #00E676; }
        
        /* 進度條顏色 */
        .stProgress > div > div > div > div { background-color: #00E676; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據庫與模擬器
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target']).to_csv(PORTFOLIO_FILE, index=False)
    if not os.path.exists(TRADE_LOG_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Action', 'Price', 'PnL']).to_csv(TRADE_LOG_FILE, index=False)

def execute_trade(action, data=None):
    init_db()
    if action == "buy" and data:
        df = pd.read_csv(PORTFOLIO_FILE)
        if data['Symbol'] in df['Symbol'].values: return "⚠️ 已持倉"
        
        qty = int(CAPITAL_PER_TRADE / data['Entry'])
        new_row = {
            'Date': datetime.date.today(), 'Symbol': data['Symbol'], 
            'Entry': data['Entry'], 'Qty': qty, 
            'Stop': data['Stop'], 'Target': data['Target']
        }
        pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
        return f"✅ 買入 {data['Symbol']} @ {data['Entry']:.2f}"
    return "OK"

# ==========================================
# 3. 數據源：S&P 500 全市場
# ==========================================
@st.cache_data
def get_sp500_tickers():
    # 這裡從 Wikipedia 抓取 S&P 500 成分股，保證數量足夠
    # 為了演示速度，如果抓取失敗，我們使用一個較大的內建列表
    try:
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        df = table[0]
        tickers = df['Symbol'].tolist()
        return [t.replace('.', '-') for t in tickers] # 修正 BRK.B
    except:
        # 後備名單 (100隻)
        return ["NVDA", "MSFT", "AAPL", "AMZN", "META", "GOOGL", "TSLA", "AVGO", "AMD", "JPM", "V", "LLY", "WMT", "XOM", "UNH", "MA", "PG", "COST", "JNJ", "HD", "MRK", "ABBV", "CVX", "CRM", "BAC", "KO", "NFLX", "PEP", "ADBE", "TMO", "LIN", "WFC", "ACN", "MCD", "DIS", "CSCO", "ABT", "INTC", "QCOM", "VZ", "CMCSA", "INTU", "AMAT", "IBM", "PFE", "UBER", "TXN", "AMGN", "NOW", "CAT", "SPGI", "GE", "PM", "UNP", "GS", "ISRG", "LOW", "COP", "PLTR", "HON", "RTX", "BKNG", "T", "AXP", "NEE", "ELV", "ETN", "BLK", "SYK", "PGR", "TJX", "MS", "C", "VRTX", "REGN", "BSX", "BA", "PANW", "ADP", "MMC", "CB", "MDLZ", "KLAC", "GILD", "LRCX", "ADI", "AMT", "LMT", "CI", "CVS", "SCHW", "SNOW", "SQ", "COIN", "MSTR", "DKNG", "HOOD", "RIVN", "LCID"]

@st.cache_data(ttl=600)
def fetch_bulk_data(tickers):
    # 分批下載以防超時
    data = yf.download(tickers, period="6mo", group_by='ticker', threads=True, progress=False)
    return data

# ==========================================
# 4. 綜合技術評分 (Best Technical Analysis)
# ==========================================
def calculate_comprehensive_score(ticker, df):
    # 這是真正的全方位技術分析
    try:
        if len(df) < 100: return None
        
        # 1. 數據準備
        close = df['Close']
        high = df['High']
        low = df['Low']
        vol = df['Volume']
        curr = float(close.iloc[-1])
        
        # 2. 指標計算
        # EMA
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1])
        ema200 = float(close.ewm(span=200).mean().iloc[-1])
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        rsi_val = float(rsi.iloc[-1])
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val = float(macd.iloc[-1])
        sig_val = float(signal.iloc[-1])
        
        # Bollinger Bands (布林帶)
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = sma20 + (std20 * 2)
        lower = sma20 - (std20 * 2)
        bb_upper = float(upper.iloc[-1])
        bb_lower = float(lower.iloc[-1])
        
        # ATR (波動率)
        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        
        # 量能
        vol_avg = float(vol.rolling(50).mean().iloc[-1])
        rvol = float(vol.iloc[-1]) / vol_avg if vol_avg > 0 else 0
        
        # 3. 評分邏輯 (滿分 100)
        score = 0
        reasons = []
        
        # A. 趨勢 (30分)
        if curr > ema20 > ema50: 
            score += 20
            reasons.append("EMA 多頭排列")
        if curr > ema200: 
            score += 10
            reasons.append("長期趨勢向上 (Above EMA200)")
            
        # B. 動能 (30分)
        if macd_val > sig_val:
            score += 15
            reasons.append("MACD 黃金交叉")
        if 50 < rsi_val < 70:
            score += 15
            reasons.append(f"RSI 強勢區 ({rsi_val:.1f})")
            
        # C. 波動與突破 (20分)
        if curr > bb_upper * 0.98: # 接近或突破上軌
            score += 20
            reasons.append("布林帶突破 (BB Breakout)")
            
        # D. 資金流 (20分)
        if rvol > 1.2:
            score += 20
            reasons.append(f"爆量上漲 (Vol {rvol:.1f}x)")
        elif rvol > 0.8:
            score += 10
            
        # 4. 進場與止損邏輯
        setup = "盤整"
        if "布林帶突破" in str(reasons):
            setup = "突破交易 (Breakout)"
            entry = curr
            stop = ema20 # 趨勢線止損
        elif "EMA 多頭排列" in str(reasons) and rsi_val < 60:
            setup = "趨勢回調 (Pullback)"
            entry = curr
            stop = curr - (2 * atr) # 波動率止損
        else:
            setup = "觀察 (Watch)"
            entry = curr
            stop = curr * 0.95
            
        target = entry + (3 * (entry - stop))
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Price": curr,
            "RSI": rsi_val,
            "MACD_Hist": macd_val - sig_val,
            "Setup": setup,
            "Entry": entry,
            "Stop": stop,
            "Target": target,
            "Reasons": ", ".join(reasons)
        }
        
    except: return None

# ==========================================
# 5. 主程式介面
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.header("🦅 J LAW ALPHA: S&P 500")
    menu = st.radio("系統模組", ["⚡ 全市場掃描 (Scanner)", "📈 資產管理 (Portfolio)"])
    st.info("系統提示：正在掃描 S&P 500 及熱門股。所有結果將依評分排序，絕不遺漏。")

if menu == "⚡ 全市場掃描 (Scanner)":
    st.title("⚡ S&P 500 全市場技術掃描")
    
    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        start_scan = st.button("🚀 啟動全市場分析", use_container_width=True)
    
    if start_scan:
        status = st.empty()
        status.info("正在獲取 S&P 500 股票清單...")
        tickers = get_sp500_tickers()
        
        status.info(f"正在下載 {len(tickers)} 隻股票數據 (這可能需要 30 秒)...")
        data = fetch_bulk_data(tickers)
        
        results = []
        bar = st.progress(0)
        
        # 執行分析
        for i, t in enumerate(tickers):
            try:
                df_t = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                res = calculate_comprehensive_score(t, df_t)
                if res: results.append(res)
            except: pass
            
            # 每 10% 更新一次進度條以節省資源
            if i % (len(tickers)//20) == 0:
                bar.progress((i+1)/len(tickers))
        
        bar.empty()
        status.success(f"掃描完成！分析了 {len(results)} 隻股票。")
        
        # 儲存並排序 (由高分到低分)
        st.session_state['sp500_results'] = pd.DataFrame(results).sort_values('Score', ascending=False)

    # 顯示結果
    if 'sp500_results' in st.session_state:
        df = st.session_state['sp500_results']
        
        # 上半部：篩選與列表
        c1, c2 = st.columns([1.5, 3])
        
        with c1:
            st.markdown("### 🏆 市場排名")
            # 顯示前 50 名，防止列表過長，但允許查看更多
            top_n = st.slider("顯示數量", 10, 200, 50)
            df_display = df.head(top_n)
            
            # 使用 Emoji 代表分數等級
            def get_icon(s):
                if s >= 80: return "🔥"
                if s >= 60: return "✅"
                return "👀"
                
            sel = st.radio("選擇標的 (按分數排序)", df_display['Symbol'].tolist(), 
                         format_func=lambda x: f"{get_icon(df[df['Symbol']==x]['Score'].values[0])} {x} - {df[df['Symbol']==x]['Score'].values[0]}分",
                         label_visibility="collapsed")
            
        with c2:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                
                # 詳細分析面板
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:10px;">
                    <div>
                        <h1 style="margin:0; color:#fff; font-size:48px;">{row['Symbol']}</h1>
                        <span style="color:#00E676; font-weight:bold;">{row['Setup']}</span>
                    </div>
                    <div class="score-box">{row['Score']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # 四宮格數據
                st.markdown(f"""
                <div class="data-grid" style="margin-top:15px;">
                    <div class="data-card"><div class="data-label">現價 Price</div><div class="data-value">${row['Price']:.2f}</div></div>
                    <div class="data-card"><div class="data-label">RSI (14)</div><div class="data-value" style="color:{'#00E676' if 50<row['RSI']<70 else '#fff'}">{row['RSI']:.1f}</div></div>
                    <div class="data-card"><div class="data-label">MACD Hist</div><div class="data-value" style="color:{'#00E676' if row['MACD_Hist']>0 else '#FF1744'}">{row['MACD_Hist']:.2f}</div></div>
                    <div class="data-card"><div class="data-label">建議進場</div><div class="data-value" style="color:#00E676">${row['Entry']:.2f}</div></div>
                </div>
                """, unsafe_allow_html=True)
                
                # 買賣按鈕與策略
                c_act, c_txt = st.columns([1, 1.5])
                with c_act:
                    st.markdown(f"""
                    <div style="background:#1a1a1a; padding:15px; border-radius:5px; border:1px solid #444;">
                        <span style="color:#888; font-size:12px;">交易計劃 (Trade Plan)</span><br>
                        <div style="display:flex; justify-content:space-between; margin-top:5px;">
                            <span>止損 Stop:</span> <span style="color:#FF1744; font-weight:bold;">${row['Stop']:.2f}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between;">
                            <span>目標 Target:</span> <span style="color:#00E676; font-weight:bold;">${row['Target']:.2f}</span>
                        </div>
                        <div style="margin-top:10px; font-size:12px; color:#aaa;">R:R Ratio: 1:3</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"⚡ 模擬買入 {row['Symbol']}", use_container_width=True):
                        msg = execute_trade("buy", row)
                        st.success(msg)
                
                with c_txt:
                    st.markdown("### 📊 技術解碼")
                    st.write(f"**觸發條件:** {row['Reasons']}")
                    st.caption("分析結合了：EMA 趨勢排列、MACD 動能、RSI 強弱區間、布林帶突破及成交量分析。")
                
                # 圖表
                components.html(f"""
                <div class="tradingview-widget-container" style="height:500px;width:100%">
                  <div id="tv_{row['Symbol']}" style="height:100%"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                    "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                    "toolbar_bg": "#000", "enable_publishing": false, 
                    "studies": ["MACD@tv-basicstudies", "RSI@tv-basicstudies", "BB@tv-basicstudies"],
                    "container_id": "tv_{row['Symbol']}"
                  }});
                  </script>
                </div>
                """, height=500)

elif menu == "📈 資產管理 (Portfolio)":
    st.title("📈 我的交易組合")
    
    if os.path.exists(PORTFOLIO_FILE):
        df = pd.read_csv(PORTFOLIO_FILE)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # 簡單盈虧預覽 (需要連網更新現價，這裡做靜態展示)
            st.info("💡 提示：此頁面記錄你的模擬交易。請定期回到掃描器檢查最新買賣點。")
        else:
            st.info("目前沒有持倉。請到掃描器尋找高分股票。")
    else:
        st.info("數據庫初始化中...")
