import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components
import base64
import os
import datetime

# ==========================================
# 0. 系統基礎設定
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 模擬器檔案路徑
PORTFOLIO_FILE = 'sim_portfolio.csv'
TRADE_LOG_FILE = 'sim_trade_log.csv'
CAPITAL_PER_TRADE = 10000  # 每次模擬投入金額 (USD)

# ==========================================
# 1. CSS 與視覺核心
# ==========================================
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return None

def inject_css():
    img_file = "tesla_bg.jpg" 
    bin_str = get_base64_of_bin_file(img_file)
    if bin_str:
        bg_image_css = f'url("data:image/jpg;base64,{bin_str}")'
    else:
        bg_image_css = 'url("https://images.hdqwalls.com/wallpapers/tesla-logo-red-4k-yu.jpg")'

    overlay = "radial-gradient(circle, rgba(0,0,0,0.4) 0%, rgba(0,0,0,0.95) 85%)"

    style_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');
        .stApp {{
            background-image: {overlay}, {bg_image_css};
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #E0E0E0;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        section[data-testid="stSidebar"] {{
            background: rgba(5, 5, 5, 0.9);
            border-right: 1px solid #333;
            backdrop-filter: blur(10px);
        }}
        h1, h2, h3, h4, span, div {{ text-shadow: 0 2px 4px rgba(0,0,0,0.9); }}
        div[role="radiogroup"] > label {{
            background: rgba(0,0,0,0.6); border: 1px solid #333; color: #aaa;
            transition: all 0.2s; font-family: 'JetBrains Mono';
        }}
        div[role="radiogroup"] > label:hover {{
            border-color: #E53935; color: #fff; background: rgba(229, 57, 53, 0.2);
        }}
        div[role="radiogroup"] > label[data-checked="true"] {{
            background: #000 !important; border: 1px solid #E53935; color: #E53935 !important; font-weight: 700;
        }}
        .stat-card {{
            background: rgba(20,20,20,0.7); border: 1px solid #444; padding: 12px;
            border-radius: 6px; text-align: center; height: 100%; backdrop-filter: blur(5px);
        }}
        .stat-label {{ font-size: 11px; color: #999; letter-spacing: 1px; text-transform: uppercase; }}
        .stat-value {{ font-size: 22px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono'; }}
        .report-panel {{
            background: rgba(0, 0, 0, 0.75); border: 1px solid #444; border-left: 4px solid #E53935;
            padding: 20px; border-radius: 4px; line-height: 1.7; backdrop-filter: blur(5px);
        }}
        div.stButton > button {{
            background: rgba(0,0,0,0.5); border: 1px solid #E53935; color: #E53935; font-weight: bold;
        }}
        div.stButton > button:hover {{
            background: rgba(229, 57, 53, 0.3); color: #fff; border-color: #fff;
        }}
        /* 表格樣式優化 */
        [data-testid="stDataFrame"] {{ background: rgba(0,0,0,0.6); border-radius: 5px; padding: 10px; }}
    </style>
    """
    st.markdown(style_code, unsafe_allow_html=True)

# ==========================================
# 2. 模擬器核心邏輯 (Simulator Engine)
# ==========================================
def init_sim_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry_Price', 'Qty', 'Stop_Loss', 'Take_Profit', 'Status']).to_csv(PORTFOLIO_FILE, index=False)
    if not os.path.exists(TRADE_LOG_FILE):
        pd.DataFrame(columns=['Buy_Date', 'Sell_Date', 'Symbol', 'Entry_Price', 'Exit_Price', 'Profit_Loss', 'Result']).to_csv(TRADE_LOG_FILE, index=False)

def add_to_portfolio(row):
    init_sim_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    
    # 避免重複下單
    if row['Symbol'] in df['Symbol'].values:
        return False, "已在持倉中"
        
    qty = int(CAPITAL_PER_TRADE / row['Entry'])
    new_trade = {
        'Date': datetime.date.today(),
        'Symbol': row['Symbol'],
        'Entry_Price': round(row['Entry'], 2),
        'Qty': qty,
        'Stop_Loss': round(row['Stop'], 2),
        'Take_Profit': round(row['Target'], 2),
        'Status': 'OPEN'
    }
    df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
    df.to_csv(PORTFOLIO_FILE, index=False)
    return True, f"已以 ${row['Entry']:.2f} 買入 {qty} 股"

def check_portfolio_logic():
    init_sim_db()
    open_pos = pd.read_csv(PORTFOLIO_FILE)
    trade_log = pd.read_csv(TRADE_LOG_FILE)
    
    if open_pos.empty: return "目前無持倉", open_pos, trade_log

    updated_pos = []
    messages = []
    
    # 批量獲取現價以加快速度
    tickers = open_pos['Symbol'].tolist()
    try:
        # 下載即時數據
        data = yf.download(tickers, period="1d", progress=False)['Close']
        if isinstance(data, pd.Series): data = data.to_frame().T # 處理單一股票情況
        
        current_prices = {}
        # 處理 yfinance 下載格式可能的問題
        for t in tickers:
            try:
                if len(tickers) == 1:
                    price = float(data.iloc[-1])
                else:
                    price = float(data[t].iloc[-1])
                current_prices[t] = price
            except:
                current_prices[t] = None
                
    except Exception as e:
        return f"行情更新失敗: {str(e)}", open_pos, trade_log

    for index, row in open_pos.iterrows():
        sym = row['Symbol']
        curr_price = current_prices.get(sym)
        
        if not curr_price or np.isnan(curr_price):
            updated_pos.append(row) # 價格抓不到，保持原樣
            continue
            
        action = None
        if curr_price <= row['Stop_Loss']: action = "STOP_LOSS"
        elif curr_price >= row['Take_Profit']: action = "TAKE_PROFIT"
        
        if action:
            pnl = (curr_price - row['Entry_Price']) * row['Qty']
            result = 'WIN' if pnl > 0 else 'LOSS'
            
            log_entry = {
                'Buy_Date': row['Date'],
                'Sell_Date': datetime.date.today(),
                'Symbol': sym,
                'Entry_Price': row['Entry_Price'],
                'Exit_Price': round(curr_price, 2),
                'Profit_Loss': round(pnl, 2),
                'Result': result
            }
            trade_log = pd.concat([trade_log, pd.DataFrame([log_entry])], ignore_index=True)
            messages.append(f"⚠️ {sym} 觸發 {action}！以 ${curr_price:.2f} 賣出，損益: ${pnl:.2f}")
        else:
            updated_pos.append(row) # 繼續持有

    # 存回 CSV
    pd.DataFrame(updated_pos, columns=open_pos.columns).to_csv(PORTFOLIO_FILE, index=False)
    trade_log.to_csv(TRADE_LOG_FILE, index=False)
    
    return messages, pd.DataFrame(updated_pos), trade_log

# ==========================================
# 3. 數據與指標計算
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

def analyze_stock_pro(ticker, df):
    try:
        if df is None or len(df) < 200: return None
        df = df.sort_index()
        curr = df.iloc[-1]
        
        try:
            close = extract_scalar(curr['Close'])
            high = extract_scalar(curr['High'])
            low = extract_scalar(curr['Low'])
            vol = extract_scalar(curr['Volume'])
        except: return None
        
        close_s = df['Close'] if isinstance(df['Close'], pd.Series) else df['Close'].iloc[:, 0]
        ma10 = extract_scalar(close_s.rolling(10).mean().iloc[-1])
        ma20 = extract_scalar(close_s.rolling(20).mean().iloc[-1])
        ma50 = extract_scalar(close_s.rolling(50).mean().iloc[-1])
        ma200 = extract_scalar(close_s.rolling(200).mean().iloc[-1])
        
        high_s = df['High'] if isinstance(df['High'], pd.Series) else df['High'].iloc[:, 0]
        low_s = df['Low'] if isinstance(df['Low'], pd.Series) else df['Low'].iloc[:, 0]
        atr = extract_scalar((high_s - low_s).rolling(14).mean().iloc[-1])
        
        vol_s = df['Volume'] if isinstance(df['Volume'], pd.Series) else df['Volume'].iloc[:, 0]
        avg_vol = extract_scalar(vol_s.rolling(50).mean().iloc[-1])
        vol_ratio = vol / avg_vol if avg_vol > 0 else 1.0

        rsi_s = calculate_rsi(close_s)
        rsi_val = extract_scalar(rsi_s.iloc[-1])
        
        macd_s, sig_s = calculate_macd(close_s)
        macd_val = extract_scalar(macd_s.iloc[-1])
        sig_val = extract_scalar(sig_s.iloc[-1])
        macd_hist = macd_val - sig_val
        
        if close < ma200: return None
        
        pattern = ""
        score = 0
        analysis_lines = []
        
        dist_20 = (low - ma20) / ma20
        dist_10 = (low - ma10) / ma10
        dist_50 = (low - ma50) / ma50
        
        if abs(dist_20) <= 0.035 and close > ma20:
            pattern = "🎾 Tennis Ball"
            score = 90
            analysis_lines.append(f"📈 **趨勢結構**：長期多頭，回測 20MA (${ma20:.2f}) 支撐。")
        elif abs(dist_10) <= 0.025 and close > ma10:
            pattern = "🔥 Power Trend"
            score = 95
            analysis_lines.append(f"📈 **趨勢結構**：超級強勢！沿 10MA (${ma10:.2f}) 噴出。")
        elif abs(dist_50) <= 0.03 and close > ma50:
            pattern = "🛡️ Base Support"
            score = 80
            analysis_lines.append(f"📈 **趨勢結構**：回測 50MA (${ma50:.2f}) 機構成本線。")
        else:
            return None 

        if rsi_val > 75: score -= 5
        elif rsi_val < 30: score += 5
        elif 50 <= rsi_val <= 70: score += 5
            
        if vol_ratio > 1.5: score += 5

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
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-end; border-bottom:1px solid #444; padding-bottom:15px; margin-bottom:15px;">
        <div>
            <span style="color:#E53935; font-size:14px; font-weight:bold;">STOCK TICKER</span><br>
            <span style="font-size:52px; font-weight:900; letter-spacing:-2px; color:#fff; font-family:'JetBrains Mono'; text-shadow: 0 0 20px rgba(229, 57, 53, 0.6);">{row['Symbol']}</span>
            <span style="background:rgba(229, 57, 53, 0.2); color:#ff6b6b; border:1px solid #E53935; padding:2px 8px; font-size:12px; margin-left:10px; border-radius:3px; vertical-align:middle;">{row['Pattern']}</span>
        </div>
        <div style="text-align:right;">
            <span style="color:#888; font-size:12px;">AI 戰術評分</span><br>
            <span style="font-size:42px; font-weight:700; color:#E53935; font-family:'JetBrains Mono';">{row['Score']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="stat-card"><div class="stat-label">現價 PRICE</div><div class="stat-value">${float(row["Close"]):.2f}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stat-card" style="border-bottom:2px solid #E53935"><div class="stat-label">買入 ENTRY</div><div class="stat-value" style="color:#ff6b6b">${float(row["Entry"]):.2f}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stat-card" style="border-bottom:2px solid #FF1744"><div class="stat-label">止蝕 STOP</div><div class="stat-value" style="color:#FF1744">${float(row["Stop"]):.2f}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="stat-card"><div class="stat-label">目標 TARGET (3R)</div><div class="stat-value">${float(row["Target"]):.2f}</div></div>', unsafe_allow_html=True)
    
    st.write("")
    
    # 這裡加入模擬買入按鈕
    if st.button(f"🤖 模擬買入 {row['Symbol']} (Entry: ${row['Entry']:.2f})", key=f"btn_buy_{row['Symbol']}"):
        success, msg = add_to_portfolio(row)
        if success:
            st.toast(msg, icon="✅")
        else:
            st.toast(msg, icon="⚠️")
    
    st.write("")
    col_text, col_chart = st.columns([1, 1.4])
    
    with col_text:
        st.markdown(f"""
        <div class="report-panel">
            <div style="border-bottom:1px solid #444; padding-bottom:10px; margin-bottom:10px;">
                <span class="report-hl">⚡ J LAW 戰術報告</span>
            </div>
            {row['Report']}
            <br>
            <div style="margin-top:10px; font-size:13px; color:#aaa;">
            RSI: {row['RSI']:.1f} | RVOL: {row['Vol_Ratio']:.1f}x | R:R: 1:{row['RR']:.1f}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with col_chart:
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:500px;width:100%">
          <div id="tv_{row['Symbol']}" style="height:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
            "locale": "zh_TW", "toolbar_bg": "#000", "enable_publishing": false, "hide_side_toolbar": false, "allow_symbol_change": true,
            "container_id": "tv_{row['Symbol']}",
            "studies": ["MASimple@tv-basicstudies", "RSI@tv-basicstudies"]
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=510)

# ==========================================
# 4. 主程式邏輯
# ==========================================
if 'scan_data' not in st.session_state: st.session_state['scan_data'] = None
if 'watchlist' not in st.session_state: st.session_state['watchlist'] = ["TSLA", "NVDA", "MSTR"]

inject_css()
init_sim_db()

with st.sidebar:
    st.markdown("### 🦅 ALPHA STATION <span style='font-size:10px; color:#E53935; border:1px solid #E53935; padding:1px 3px;'>V19.0 Sim</span>", unsafe_allow_html=True)
    mode = st.radio("系統模組", ["⚡ 強勢股掃描器", "🤖 戰術模擬器", "👀 觀察名單", "🚨 TSLA 戰情室"])
    
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
    st.title("⚡ 強勢股掃描器")
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

elif mode == "🤖 戰術模擬器":
    st.title("🤖 模擬交易實驗室 (Paper Trading)")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("🔄 更新行情 & 檢查止盈止損", use_container_width=True):
        with st.spinner("正在連接交易所..."):
            msgs, _, _ = check_portfolio_logic()
            if isinstance(msgs, list) and msgs:
                for m in msgs: st.error(m)
            elif isinstance(msgs, list) and not msgs:
                st.success("持倉檢查完畢，無觸發事件。")
            else:
                st.error(msgs)
    
    if c2.button("🗑️ 重置所有模擬數據", use_container_width=True):
        if os.path.exists(PORTFOLIO_FILE): os.remove(PORTFOLIO_FILE)
        if os.path.exists(TRADE_LOG_FILE): os.remove(TRADE_LOG_FILE)
        init_sim_db()
        st.rerun()

    st.markdown("---")
    
    # 讀取數據
    open_pos = pd.read_csv(PORTFOLIO_FILE)
    trade_log = pd.read_csv(TRADE_LOG_FILE)
    
    # 1. 持倉區
    st.subheader(f"📈 目前持倉 ({len(open_pos)})")
    if not open_pos.empty:
        st.dataframe(open_pos, use_container_width=True)
    else:
        st.info("目前無持倉。請到掃描器中點擊「模擬買入」。")
        
    st.markdown("---")
    
    # 2. 統計區
    st.subheader("📊 績效分析")
    if not trade_log.empty:
        wins = len(trade_log[trade_log['Result'] == 'WIN'])
        losses = len(trade_log[trade_log['Result'] == 'LOSS'])
        total = wins + losses
        win_rate = (wins / total * 100) if total > 0 else 0
        total_pnl = trade_log['Profit_Loss'].sum()
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("總勝率 (Win Rate)", f"{win_rate:.1f}%")
        m2.metric("總盈虧 (P&L)", f"${total_pnl:.2f}", delta=total_pnl)
        m3.metric("勝場", str(wins))
        m4.metric("敗場", str(losses))
        
        st.write("交易歷史紀錄：")
        st.dataframe(trade_log.sort_values('Sell_Date', ascending=False), use_container_width=True)
    else:
        st.caption("尚無已平倉的交易紀錄。")

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
                    curr = extract_scalar(d['Close'].iloc[-1])
                    rsi_s = calculate_rsi(d['Close']); rsi_now = extract_scalar(rsi_s.iloc[-1])
                    st.header(f"{sel}")
                    m1, m2 = st.columns(2)
                    m1.metric("現價", f"${curr:.2f}")
                    m2.metric("RSI (14)", f"{rsi_now:.1f}")
                    st.info("⚠️ 該股目前未出現特定強勢型態，建議觀望。")
                    
                    tv_html = f"""<div class="tradingview-widget-container" style="height:500px;width:100%"><div id="tv_{sel}" style="height:100%"></div><script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script><script type="text/javascript">new TradingView.widget({{ "autosize": true, "symbol": "{sel}", "interval": "D", "theme": "dark", "style": "1", "studies": ["RSI@tv-basicstudies"], "container_id": "tv_{sel}" }});</script></div>"""
                    components.html(tv_html, height=510)

elif mode == "🚨 TSLA 戰情室":
    st.markdown("<h1 style='text-align:center; color:#fff; text-shadow:0 0 20px #E53935;'>⚡ TESLA INTELLIGENCE</h1>", unsafe_allow_html=True)
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
        
    with cr:
        st.markdown("### 💬 StockTwits Feed")
        try:
            r = requests.get("https://api.stocktwits.com/api/2/streams/symbol/TSLA.json", headers={'User-Agent':'Mozilla/5.0'}, timeout=3)
            for m in r.json().get('messages', [])[:3]:
                st.markdown(f"<div style='background:rgba(20,20,20,0.8); padding:10px; margin-bottom:5px; border-left:3px solid #E53935;'>@{m['user']['username']}: {m['body']}</div>", unsafe_allow_html=True)
        except: st.caption("Social feed unavailable.")
