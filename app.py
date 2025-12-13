import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統設定與視覺核心 (Tesla 主題)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 背景圖：Tesla Model S 紅色車尾 (暗色調，適合當背景)
GLOBAL_BG_URL = "https://images.hdqwalls.com/wallpapers/tesla-model-s-rear-4k-yu.jpg"

def inject_css():
    # 使用深黑色遮罩 (90% 透明度) 確保文字清晰，背景隱約可見
    overlay = "rgba(0,0,0,0.85), rgba(0,0,0,0.92)"

    style_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

        /* 全局背景 */
        .stApp {{
            background-image: linear-gradient({overlay}), url("{GLOBAL_BG_URL}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #E0E0E0;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        
        /* 側邊欄 */
        section[data-testid="stSidebar"] {{
            background: rgba(10, 10, 10, 0.95);
            border-right: 1px solid #333;
        }}
        
        /* Radio 按鈕優化 */
        div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}
        div[role="radiogroup"] {{ gap: 5px; }}
        
        div[role="radiogroup"] > label {{
            background: rgba(255,255,255,0.03);
            border: 1px solid #333;
            padding: 12px 15px;
            border-radius: 4px;
            transition: all 0.2s;
            font-family: 'JetBrains Mono', monospace;
            font-size: 14px;
            color: #aaa;
            cursor: pointer;
            width: 100%;
        }}
        
        div[role="radiogroup"] > label:hover {{
            border-color: #E53935;
            color: #fff;
            background: rgba(229, 57, 53, 0.1);
        }}
        
        div[role="radiogroup"] > label[data-checked="true"] {{
            background: #000 !important;
            border: 1px solid #E53935;
            box-shadow: 0 0 10px rgba(229, 57, 53, 0.3);
            color: #E53935 !important;
            font-weight: 700;
        }}

        /* 數據卡片 */
        .stat-card {{
            background: rgba(20,20,20,0.6);
            border: 1px solid #444;
            padding: 12px;
            border-radius: 6px;
            text-align: center;
            height: 100%;
            margin-bottom: 10px;
        }}
        .stat-label {{ font-size: 11px; color: #999; letter-spacing: 1px; text-transform: uppercase; }}
        .stat-value {{ font-size: 22px; font-weight: 700; color: #fff; margin-top: 2px; font-family: 'JetBrains Mono'; }}
        .stat-sub {{ font-size: 11px; color: #ccc; margin-top: 2px; }}

        /* 報告面板 */
        .report-panel {{
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #444;
            border-left: 4px solid #E53935;
            padding: 20px;
            border-radius: 4px;
            font-family: 'Noto Sans TC', sans-serif;
            line-height: 1.7;
            font-size: 15px;
            margin-bottom: 20px;
        }}
        .report-hl {{ color: #E53935; font-weight: bold; }}
        .report-green {{ color: #00E676; font-weight: bold; }}
        .report-risk {{ color: #FF1744; font-weight: bold; }}
        
        /* 按鈕樣式 */
        div.stButton > button {{
            background: transparent;
            border: 1px solid #E53935;
            color: #E53935;
            border-radius: 4px;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background: rgba(229, 57, 53, 0.1);
            color: #fff;
            border-color: #fff;
        }}
    </style>
    """
    st.markdown(style_code, unsafe_allow_html=True)

# ==========================================
# 2. 數據與指標計算 (新增 RSI, MACD)
# ==========================================
@st.cache_data
def get_market_universe():
    return [
        "NVDA", "TSLA", "MSTR", "PLTR", "COIN", "SMCI", "APP", "HOOD", 
        "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "NET",
        "CRWD", "PANW", "UBER", "ABNB", "DASH", "DKNG", "RIVN", "CVNA",
        "AFRM", "UPST", "MARA", "CLSK", "RIOT", "SOFI", "PATH", "U", "AI",
        "ARM", "MU", "QCOM", "INTC", "TSM", "CELH", "ELF", "LULU", "ONON", "HIMS"
    ]

@st.cache_data(ttl=900, show_spinner=False)
def fetch_bulk_data(tickers):
    try:
        data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
        return data
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def fetch_single_data(ticker):
    return yf.download(ticker, period="1y", progress=False)

def extract_scalar(value):
    if isinstance(value, pd.Series): return float(value.iloc[0])
    try: return float(value)
    except: return 0.0

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(series, fast=12, slow=26, signal=9):
    exp1 = series.ewm(span=fast, adjust=False).mean()
    exp2 = series.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig

# ==========================================
# 3. 核心分析邏輯 (深度升級)
# ==========================================
def analyze_stock_pro(ticker, df):
    try:
        if df is None or len(df) < 200: return None
        df = df.sort_index()
        curr = df.iloc[-1]
        
        # 1. 基礎數據
        try:
            close = extract_scalar(curr['Close'])
            high = extract_scalar(curr['High'])
            low = extract_scalar(curr['Low'])
            vol = extract_scalar(curr['Volume'])
        except: return None
        
        # 2. 技術指標計算
        close_s = df['Close'] if isinstance(df['Close'], pd.Series) else df['Close'].iloc[:, 0]
        
        # 均線
        ma10 = extract_scalar(close_s.rolling(10).mean().iloc[-1])
        ma20 = extract_scalar(close_s.rolling(20).mean().iloc[-1])
        ma50 = extract_scalar(close_s.rolling(50).mean().iloc[-1])
        ma200 = extract_scalar(close_s.rolling(200).mean().iloc[-1])
        
        # ATR & Volume
        high_s = df['High'] if isinstance(df['High'], pd.Series) else df['High'].iloc[:, 0]
        low_s = df['Low'] if isinstance(df['Low'], pd.Series) else df['Low'].iloc[:, 0]
        atr = extract_scalar((high_s - low_s).rolling(14).mean().iloc[-1])
        
        vol_s = df['Volume'] if isinstance(df['Volume'], pd.Series) else df['Volume'].iloc[:, 0]
        avg_vol = extract_scalar(vol_s.rolling(50).mean().iloc[-1])
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1.0

        # RSI & MACD (新增)
        rsi_s = calculate_rsi(close_s)
        rsi_val = extract_scalar(rsi_s.iloc[-1])
        
        macd_s, sig_s = calculate_macd(close_s)
        macd_val = extract_scalar(macd_s.iloc[-1])
        sig_val = extract_scalar(sig_s.iloc[-1])
        macd_hist = macd_val - sig_val
        
        # 3. 過濾條件 (只看年線以上)
        if close < ma200: return None
        
        pattern = ""
        score = 0
        analysis_lines = []
        
        # --- A. 型態識別 ---
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        dist_50 = (low - ma50) / ma50
        
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "🎾 Tennis Ball (網球行為)"
            score = 90
            analysis_lines.append(f"📈 **趨勢結構**：長期多頭排列，股價回測 20日均線 (${ma20:.2f}) 獲得支撐，如網球落地反彈。")
        elif abs(dist_10) <= 0.025 and close > ma10:
            pattern = "🔥 Power Trend (強力趨勢)"
            score = 95
            analysis_lines.append(f"📈 **趨勢結構**：超級強勢股特徵！股價沿著 10日均線 (${ma10:.2f}) 噴出，市場買盤極強。")
        elif abs(dist_50) <= 0.03 and close > ma50:
            pattern = "🛡️ Base Support (50MA防線)"
            score = 80
            analysis_lines.append(f"📈 **趨勢結構**：中期波段修正至 50日機構成本線 (${ma50:.2f})，這是多頭的重要防守點。")
        else:
            return None 

        # --- B. RSI 深度分析 ---
        analysis_lines.append("<br>📊 **指標診斷 (RSI & MACD)**：")
        rsi_status = ""
        if rsi_val > 75:
            rsi_status = "🔥 超買區 (Overbought)"
            analysis_lines.append(f"• **RSI ({rsi_val:.1f})**：進入{rsi_status}，短線過熱，不建議追高，適合等待回調或突破確認。")
            score -= 5
        elif rsi_val < 30:
            rsi_status = "❄️ 超賣區 (Oversold)"
            analysis_lines.append(f"• **RSI ({rsi_val:.1f})**：進入{rsi_status}，乖離過大，隨時可能有技術性反彈。")
            score += 5
        elif 50 <= rsi_val <= 70:
            rsi_status = "🚀 強勢區 (Strong)"
            analysis_lines.append(f"• **RSI ({rsi_val:.1f})**：處於多頭攻擊區 (50-70)，動能充沛且未過熱。")
            score += 5
        else:
            analysis_lines.append(f"• **RSI ({rsi_val:.1f})**：處於中性整理區間。")
            
        # --- C. MACD 分析 ---
        if macd_val > sig_val:
            if macd_val > 0:
                analysis_lines.append(f"• **MACD**：黃金交叉且在零軸上方，多頭趨勢確立。")
            else:
                analysis_lines.append(f"• **MACD**：低檔黃金交叉，可能是趨勢反轉的開始。")
        else:
            if macd_hist > -0.5: # 柱狀圖收斂
                analysis_lines.append(f"• **MACD**：雖然死叉，但綠柱狀圖收斂，賣壓可能減輕。")
            else:
                analysis_lines.append(f"• **MACD**：死亡交叉向下，動能偏弱，需小心。")

        # --- D. 量能分析 ---
        if vol_ratio < 0.75:
            analysis_lines.append(f"💧 **量能**：縮量整理 ({int(vol_ratio*100)}% 均量)，籌碼沉澱良好。")
        elif vol_ratio > 1.5:
            analysis_lines.append(f"🚀 **量能**：爆量攻擊 ({vol_ratio:.1f}x 均量)，主力資金進駐。")
            score += 5

        # 交易參數
        entry_price = high + (atr * 0.1)
        if "10MA" in pattern: stop_price = ma20 - (atr * 0.1)
        elif "20MA" in pattern: stop_price = low - (atr * 0.2)
        else: stop_price = ma50 - (atr * 0.1)
        
        if entry_price <= stop_price: stop_price = entry_price * 0.95
        
        risk_per_share = entry_price - stop_price
        target_price = entry_price + (risk_per_share * 3)
        risk_pct = (risk_per_share / entry_price) * 100
        rr_ratio = (target_price - entry_price) / risk_per_share if risk_per_share != 0 else 0
        
        return {
            "Symbol": ticker,
            "Pattern": pattern,
            "Score": score,
            "Close": close,
            "Entry": entry_price,
            "Stop": stop_price,
            "Target": target_price,
            "RiskPct": risk_pct,
            "RR": rr_ratio,
            "RSI": rsi_val,
            "MACD_Hist": macd_hist,
            "Vol_Ratio": vol_ratio,
            "Report": "<br>".join(analysis_lines)
        }
    except Exception as e:
        return None

def display_dashboard(row):
    # 標題
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #444; padding-bottom:15px; margin-bottom:15px;">
        <div>
            <span style="color:#E53935; font-size:14px; font-weight:bold;">STOCK TICKER</span><br>
            <span style="font-size:52px; font-weight:900; letter-spacing:-2px; color:#fff; font-family:'JetBrains Mono';">{row['Symbol']}</span>
            <span style="background:rgba(229, 57, 53, 0.2); color:#ff6b6b; border:1px solid #E53935; padding:2px 8px; font-size:12px; margin-left:10px; border-radius:3px; vertical-align:middle;">{row['Pattern']}</span>
        </div>
        <div style="text-align:right;">
            <span style="color:#888; font-size:12px;">AI 戰術評分</span><br>
            <span style="font-size:42px; font-weight:700; color:#E53935; font-family:'JetBrains Mono';">{row['Score']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 第一排：價格與交易計劃
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-label">現價 PRICE</div><div class="stat-value">${float(row["Close"]):.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card" style="border-bottom:2px solid #E53935"><div class="stat-label">買入 ENTRY</div><div class="stat-value" style="color:#ff6b6b">${float(row["Entry"]):.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card" style="border-bottom:2px solid #FF1744"><div class="stat-label">止蝕 STOP</div><div class="stat-value" style="color:#FF1744">${float(row["Stop"]):.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-label">目標 TARGET (3R)</div><div class="stat-value">${float(row["Target"]):.2f}</div></div>', unsafe_allow_html=True)
    
    # 第二排：技術指標儀表板 (新增)
    d1, d2, d3, d4 = st.columns(4)
    
    # RSI 顏色邏輯
    rsi_val = row['RSI']
    rsi_color = "#FF1744" if rsi_val > 70 else "#00E676" if rsi_val < 30 else "#fff"
    d1.markdown(f'<div class="stat-card"><div class="stat-label">RSI (14)</div><div class="stat-value" style="color:{rsi_color}">{rsi_val:.1f}</div><div class="stat-sub">相對強弱</div></div>', unsafe_allow_html=True)
    
    # MACD 邏輯
    macd_hist = row['MACD_Hist']
    macd_txt = "BULLISH" if macd_hist > 0 else "BEARISH"
    macd_col = "#00E676" if macd_hist > 0 else "#FF1744"
    d2.markdown(f'<div class="stat-card"><div class="stat-label">MACD 動能</div><div class="stat-value" style="color:{macd_col}; font-size:20px;">{macd_txt}</div><div class="stat-sub">趨勢強度</div></div>', unsafe_allow_html=True)
    
    # 成交量
    vol_r = row['Vol_Ratio']
    vol_txt = f"{vol_r:.1f}x"
    vol_c = "#00E676" if vol_r > 1.2 else "#888"
    d3.markdown(f'<div class="stat-card"><div class="stat-label">相對量能 (RVOL)</div><div class="stat-value" style="color:{vol_c}">{vol_txt}</div><div class="stat-sub">vs 50日均量</div></div>', unsafe_allow_html=True)

    # 風險回報
    rr = row['RR']
    d4.markdown(f'<div class="stat-card"><div class="stat-label">風險回報比 (R/R)</div><div class="stat-value">1 : {rr:.1f}</div><div class="stat-sub">預期獲利</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # 分析與圖表
    col_text, col_chart = st.columns([1, 1.4])
    
    with col_text:
        st.markdown(f"""
        <div class="report-panel">
            <div style="border-bottom:1px solid #444; padding-bottom:10px; margin-bottom:10px; display:flex; justify-content:space-between;">
                <span class="report-hl">⚡ J LAW 深度戰術報告</span>
                <span style="font-size:12px; color:#888;">AI GENERATED</span>
            </div>
            {row['Report']}
            <br><br>
            <div style="border-top:1px solid #444; padding-top:15px; color:#aaa; font-size:13px; background:rgba(255,255,255,0.02); padding:10px; border-radius:4px;">
                <span class="report-hl">🎯 執行策略 (Execution):</span><br>
                在 <b>${float(row['Entry']):.2f}</b> 設定觸價買單 (Stop Buy)。<br>
                止損設於 <b class="report-risk">${float(row['Stop']):.2f}</b> (-{row['RiskPct']:.1f}%)。<br>
                若 RSI 超過 75 或觸及目標價，建議分批止盈。
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_chart:
        # TradingView Widget
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:550px;width:100%">
          <div id="tv_{row['Symbol']}" style="height:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
            "locale": "zh_TW", "toolbar_bg": "#000", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
            "container_id": "tv_{row['Symbol']}",
            "studies": [
                "MASimple@tv-basicstudies",
                "RSI@tv-basicstudies",
                "MACD@tv-basicstudies" 
            ],
            "studies_overrides": {{ 
                "MASimple@tv-basicstudies.length": 20,
                "RSI@tv-basicstudies.length": 14
            }}
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=560)

# ==========================================
# 4. 主程式邏輯
# ==========================================
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "MSTR"]

inject_css()

with st.sidebar:
    st.markdown("### 🦅 ALPHA STATION <span style='font-size:10px; color:#E53935; border:1px solid #E53935; padding:1px 3px;'>V16.0 Ultra</span>", unsafe_allow_html=True)
    mode = st.radio("系統模組", ["⚡ 強勢股掃描器", "👀 觀察名單", "🚨 TSLA 戰情室"])
    
    st.markdown("---")
    
    if mode == "⚡ 強勢股掃描器":
        if st.button("🔥 啟動全市場掃描"):
            universe = get_market_universe()
            with st.spinner('正在連線華爾街數據庫 (Downloading)...'):
                data = fetch_bulk_data(universe)
            
            if data.empty:
                st.error("數據源連線失敗")
            else:
                results = []
                progress_bar = st.progress(0)
                total = len(universe)
                
                for i, ticker in enumerate(universe):
                    try:
                        if isinstance(data.columns, pd.MultiIndex):
                            if ticker in data.columns.levels[0]: df_tick = data[ticker].dropna(how='all')
                            else: continue
                        else: df_tick = data
                        
                        res = analyze_stock_pro(ticker, df_tick)
                        if res: results.append(res)
                    except: continue
                    finally: progress_bar.progress((i + 1) / total)
                
                progress_bar.empty()
                st.toast(f"掃描完成！發現 {len(results)} 支標的", icon="✅")
                
                if results:
                    st.session_state['scan_data'] = pd.DataFrame(results).sort_values('Score', ascending=False)
                else:
                    st.session_state['scan_data'] = pd.DataFrame()
        
        if st.button("🧹 清除緩存 (Reload)"):
            st.cache_data.clear()
            st.rerun()

# 頁面渲染
if mode == "⚡ 強勢股掃描器":
    st.title("⚡ 強勢股掃描器 (Scanner)")
    df = st.session_state['scan_data']
    
    if df is None:
        st.info("系統待命。請點擊左側 [ 🔥 啟動全市場掃描 ] 。", icon="🦅")
    elif df.empty:
        st.warning("⚠️ 掃描完成：今日市場環境較差，未發現符合標準的標的。")
    else:
        c_list, c_main = st.columns([1, 3.5])
        with c_list:
            st.markdown(f"<div style='margin-bottom:10px; color:#E53935; font-weight:bold; font-size:14px;'>掃描結果 ({len(df)})</div>", unsafe_allow_html=True)
            
            fmt_map = {row['Symbol']: f"{row['Symbol']}  [{row['Score']}]" for idx, row in df.iterrows()}
            sel = st.radio("Results", df['Symbol'].tolist(), 
                         format_func=lambda x: fmt_map.get(x, x),
                         label_visibility="collapsed")
        with c_main:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                display_dashboard(row)

elif mode == "👀 觀察名單":
    st.title("👀 我的觀察名單")
    c1, c2 = st.columns([1, 3.5])
    with c1:
        new_t = st.text_input("輸入代碼 (e.g. AAPL)", "").upper()
        if st.button("➕ 新增", use_container_width=True) and new_t:
            if new_t not in st.session_state['watchlist']: 
                st.session_state['watchlist'].append(new_t)
        st.markdown("---")
        sel = st.radio("List", st.session_state['watchlist'], label_visibility="collapsed")
        
    with c2:
        if sel:
            d = fetch_single_data(sel)
            if not d.empty:
                r = analyze_stock_pro(sel, d)
                if r: display_dashboard(r)
                else:
                    # 簡易顯示模式 (當無策略訊號時)
                    curr = extract_scalar(d['Close'].iloc[-1])
                    rsi_s = calculate_rsi(d['Close']); rsi_now = extract_scalar(rsi_s.iloc[-1])
                    st.header(f"{sel}")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("現價", f"${curr:.2f}")
                    m2.metric("RSI (14)", f"{rsi_now:.1f}")
                    m3.info("目前無特定型態訊號")
                    
                    tv_html = f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "studies": ["RSI@tv-basicstudies"], "container_id": "tv_{sel}" }});</script></div>"""
                    components.html(tv_html, height=510)

elif mode == "🚨 TSLA 戰情室":
    st.markdown("<h1 style='text-align:center; color:#fff; text-shadow:0 0 20px #E53935;'>⚡ TESLA INTELLIGENCE</h1>", unsafe_allow_html=True)
    
    # 快捷區
    c1,c2,c3 = st.columns(3)
    c1.link_button("📰 Google News", "https://www.google.com/search?q=Tesla+stock&tbm=nws", use_container_width=True)
    c2.link_button("🐦 Elon Musk X", "https://twitter.com/elonmusk", use_container_width=True)
    c3.link_button("📈 TradingView", "https://www.tradingview.com/chart/?symbol=TSLA", use_container_width=True)
    st.divider()
    
    cl, cr = st.columns([1.2, 2])
    with cl:
        try:
            t = yf.Ticker("TSLA")
            h = t.history(period="1d")
            if not h.empty:
                curr = extract_scalar(h['Close'].iloc[-1])
                op = extract_scalar(h['Open'].iloc[0])
                clr = "#00E676" if curr >= op else "#FF1744"
                pct = ((curr - op) / op) * 100
                st.markdown(f"""
                <div style='text-align:center; background:rgba(0,0,0,0.6); padding:30px; border:1px solid {clr}; border-radius:8px;'>
                    <div style='color:#ccc; font-size:14px;'>REAL-TIME PRICE</div>
                    <h1 style='color:{clr}; font-size:56px; margin:0; font-family:JetBrains Mono;'>${curr:.2f}</h1>
                    <div style='color:{clr}; font-size:18px;'>{pct:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
        except: pass
        components.html("""<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{ "symbol": "NASDAQ:TSLA", "width": "100%", "height": "350", "dateRange": "12M", "colorTheme": "dark", "isTransparent": true, "autosize": false, "largeChartUrl": "" }</script></div>""", height=360)
        
    with cr:
        st.markdown("### 💬 StockTwits 討論流")
        try:
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/TSLA.json", headers={'User-Agent':'Mozilla/5.0'}, timeout=3)
            for m in r.json().get('messages', [])[:5]:
                u = m['user']['username']
                b = m['body']
                st.markdown(f"<div style='background:rgba(20,20,20,0.8); padding:15px; margin-bottom:10px; border-radius:6px; border-left:3px solid #E53935; font-size:14px;'><strong style='color:#E53935'>@{u}</strong><br><span style='color:#ccc'>{b}</span></div>", unsafe_allow_html=True)
        except: st.info("Loading Social Data...")
