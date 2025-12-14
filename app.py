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
st.set_page_config(page_title="J Law Alpha Station Pro", layout="wide", page_icon="🦅")

# 模擬器設定
PORTFOLIO_FILE = 'sim_portfolio.csv'
TRADE_LOG_FILE = 'sim_trade_log.csv'
CAPITAL_PER_TRADE = 10000  # 每次模擬投入金額 (USD)

# ==========================================
# 1. 視覺核心 (高清修復版)
# ==========================================
def inject_css():
    # 使用高清深色科技背景，移除模糊濾鏡
    bg_url = "https://images.unsplash.com/photo-1639322537228-ad7117a76432?q=80&w=2532&auto=format&fit=crop"
    
    style_code = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 全局設定 */
        .stApp {{
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.8)), url("{bg_url}");
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
            color: #E0E0E0;
            font-family: 'Noto Sans TC', sans-serif;
        }}
        
        /* 側邊欄優化 */
        section[data-testid="stSidebar"] {{
            background: #0a0a0a;
            border-right: 1px solid #333;
        }}
        
        /* 數據卡片 (更清晰) */
        .stat-card {{
            background: #1a1a1a;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .stat-label {{ font-size: 12px; color: #888; font-weight: bold; letter-spacing: 1px; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #fff; font-family: 'JetBrains Mono'; margin-top: 5px; }}
        .stat-sub {{ font-size: 11px; color: #666; margin-top: 2px; }}

        /* 分析報告區塊 */
        .strategy-box {{
            background: rgba(20, 20, 20, 0.9);
            border: 1px solid #444;
            border-left: 4px solid #00E676;
            padding: 20px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .reason-title {{ color: #00E676; font-weight: bold; font-size: 16px; margin-bottom: 10px; display: block; }}
        .reason-item {{ display: block; margin-bottom: 5px; font-size: 14px; color: #ddd; }}
        
        /* 按鈕樣式 */
        div.stButton > button {{
            background: #222;
            border: 1px solid #555;
            color: #eee;
            border-radius: 4px;
            font-weight: bold;
            transition: all 0.2s;
        }}
        div.stButton > button:hover {{
            border-color: #00E676;
            color: #00E676;
            background: rgba(0, 230, 118, 0.1);
        }}
        
        /* 表格優化 */
        [data-testid="stDataFrame"] {{ background: #111; border: 1px solid #333; }}
    </style>
    """
    st.markdown(style_code, unsafe_allow_html=True)

# ==========================================
# 2. 模擬器核心邏輯
# ==========================================
def init_sim_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry_Price', 'Qty', 'Stop_Loss', 'Take_Profit', 'Status']).to_csv(PORTFOLIO_FILE, index=False)
    if not os.path.exists(TRADE_LOG_FILE):
        pd.DataFrame(columns=['Buy_Date', 'Sell_Date', 'Symbol', 'Entry_Price', 'Exit_Price', 'Profit_Loss', 'Result']).to_csv(TRADE_LOG_FILE, index=False)

def add_to_portfolio(row):
    init_sim_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    if row['Symbol'] in df['Symbol'].values: return False, "已在持倉中"
    
    qty = int(CAPITAL_PER_TRADE / row['Entry'])
    new_trade = {
        'Date': datetime.date.today(),
        'Symbol': row['Symbol'],
        'Entry_Price': row['Entry'],
        'Qty': qty,
        'Stop_Loss': row['Stop'],
        'Take_Profit': row['Target'],
        'Status': 'OPEN'
    }
    df = pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True)
    df.to_csv(PORTFOLIO_FILE, index=False)
    return True, f"已以 ${row['Entry']:.2f} 買入 {qty} 股 {row['Symbol']}"

def check_portfolio_logic():
    init_sim_db()
    open_pos = pd.read_csv(PORTFOLIO_FILE)
    trade_log = pd.read_csv(TRADE_LOG_FILE)
    if open_pos.empty: return [], open_pos, trade_log

    updated_pos = []
    messages = []
    
    # 批量獲取價格
    tickers = open_pos['Symbol'].tolist()
    try:
        data = yf.download(tickers, period="1d", progress=False)['Close']
        current_prices = {}
        for t in tickers:
            try:
                val = float(data.iloc[-1]) if len(tickers) == 1 else float(data[t].iloc[-1])
                current_prices[t] = val
            except: current_prices[t] = None
    except: return ["網絡錯誤，無法更新價格"], open_pos, trade_log

    for _, row in open_pos.iterrows():
        sym = row['Symbol']
        curr = current_prices.get(sym)
        if not curr: 
            updated_pos.append(row)
            continue
            
        # 賣出邏輯
        action = None
        if curr <= row['Stop_Loss']: action = "STOP (止蝕)"
        elif curr >= row['Take_Profit']: action = "PROFIT (止盈)"
        
        if action:
            pnl = (curr - row['Entry_Price']) * row['Qty']
            res = 'WIN' if pnl > 0 else 'LOSS'
            log_entry = {
                'Buy_Date': row['Date'],
                'Sell_Date': datetime.date.today(),
                'Symbol': sym,
                'Entry_Price': row['Entry_Price'],
                'Exit_Price': round(curr, 2),
                'Profit_Loss': round(pnl, 2),
                'Result': res
            }
            trade_log = pd.concat([trade_log, pd.DataFrame([log_entry])], ignore_index=True)
            messages.append(f"⚠️ {sym} 觸發 {action} @ {curr:.2f} | 損益: ${pnl:.2f}")
        else:
            updated_pos.append(row)

    pd.DataFrame(updated_pos, columns=open_pos.columns).to_csv(PORTFOLIO_FILE, index=False)
    trade_log.to_csv(TRADE_LOG_FILE, index=False)
    return messages, pd.DataFrame(updated_pos), trade_log

# ==========================================
# 3. 高階指標計算 (含 DRSI / Stoch RSI)
# ==========================================
@st.cache_data
def get_market_universe():
    return ["NVDA", "TSLA", "MSTR", "PLTR", "COIN", "SMCI", "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "CRWD", "UBER", "ABNB", "DKNG", "MARA", "CLSK", "RIOT", "SOFI", "AI", "ARM", "MU", "QCOM", "TSM"]

@st.cache_data(ttl=900)
def fetch_data(tickers):
    return yf.download(tickers, period="6mo", group_by='ticker', threads=True, progress=False)

def calc_indicators(df):
    try:
        # 確保是 Series
        close = df['Close'] if isinstance(df['Close'], pd.Series) else df['Close'].iloc[:,0]
        high = df['High'] if isinstance(df['High'], pd.Series) else df['High'].iloc[:,0]
        low = df['Low'] if isinstance(df['Low'], pd.Series) else df['Low'].iloc[:,0]
        vol = df['Volume'] if isinstance(df['Volume'], pd.Series) else df['Volume'].iloc[:,0]
        
        # 1. 均線
        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()
        
        # 2. RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 3. DRSI (Stochastic RSI) - 精準買點指標
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        stoch_k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        stoch_d = stoch_k.rolling(3).mean() # Signal Line
        
        # 4. ATR (波動率 for 止損)
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(14).mean()
        
        # 5. 量能
        vol_ma = vol.rolling(50).mean()
        rvol = vol / vol_ma
        
        return {
            "Close": close.iloc[-1], "High": high.iloc[-1], "Low": low.iloc[-1],
            "MA20": ma20.iloc[-1], "MA50": ma50.iloc[-1], "MA200": ma200.iloc[-1],
            "RSI": rsi.iloc[-1], "StochK": stoch_k.iloc[-1], "StochD": stoch_d.iloc[-1],
            "ATR": atr.iloc[-1], "RVOL": rvol.iloc[-1]
        }
    except: return None

# ==========================================
# 4. 分析引擎 (Strategy Engine)
# ==========================================
def analyze_stock_pro(ticker, df):
    if df is None or len(df) < 100: return None
    
    ind = calc_indicators(df)
    if not ind: return None
    
    close = ind['Close']
    ma20, ma50, ma200 = ind['MA20'], ind['MA50'], ind['MA200']
    rsi, k, d = ind['RSI'], ind['StochK'], ind['StochD']
    atr, rvol = ind['ATR'], ind['RVOL']
    
    # --- 核心篩選條件 (嚴格) ---
    score = 0
    reasons = []
    setup_quality = "中性"
    
    # 1. 趨勢過濾 (Trend)
    if close < ma50: return None # 必須在50日線之上才看
    
    # 2. 型態識別
    is_trend_strong = (close > ma20) and (ma20 > ma50)
    is_pullback = (close < ma20 * 1.02) and (close > ma20 * 0.98) # 回測20MA附近
    
    if is_trend_strong:
        score += 50
        if is_pullback:
            reasons.append(f"✅ **趨勢回調 (Pullback)**：股價強勢回測 20MA (${ma20:.2f})，潛在支撐位。")
            score += 20
        else:
            reasons.append(f"✅ **多頭排列**：股價位於所有均線之上，動能強勁。")
    
    # 3. DRSI (Stoch RSI) 精準訊號
    # 黃金交叉: K 線由下往上穿過 D 線
    drsi_cross = (k > d) and (k < 80) # 非超買區的金叉
    drsi_oversold = (k < 20)
    
    if drsi_cross:
        reasons.append(f"⚡ **DRSI 訊號**：Stoch RSI 黃金交叉 (K:{k:.1f} > D:{d:.1f})，短線轉強訊號。")
        score += 20
    if drsi_oversold:
        reasons.append(f"📉 **DRSI 超賣**：數值低於 20，隨時準備反彈。")
        score += 10
        
    # 4. 量能與波動
    if rvol > 1.2:
        reasons.append(f"📊 **量能異常**：成交量放大 ({rvol:.1f}x)，主力介入跡象。")
        score += 10
        
    if score < 70: return None # 分數太低不顯示
    
    # --- 交易計劃生成 (Plan) ---
    # 止損：取 ATR 的 2倍 或 關鍵均線下方
    stop_loss = ma20 - (atr * 0.5) if is_pullback else close - (atr * 2)
    entry_price = close
    risk = entry_price - stop_loss
    target_price = entry_price + (risk * 2.5) # 盈虧比 2.5
    rr = (target_price - entry_price) / risk if risk > 0 else 0
    
    return {
        "Symbol": ticker,
        "Score": score,
        "Close": close,
        "Entry": entry_price,
        "Stop": stop_loss,
        "Target": target_price,
        "RR": rr,
        "RSI": rsi,
        "StochK": k,
        "StochD": d,
        "Reasons": reasons
    }

# ==========================================
# 5. UI 顯示組件
# ==========================================
def display_pro_dashboard(row):
    # 標題區
    c_title, c_score = st.columns([3, 1])
    with c_title:
        st.markdown(f"<h1 style='margin:0; font-size:48px; color:#fff;'>{row['Symbol']}</h1>", unsafe_allow_html=True)
        st.markdown(f"<span style='color:#00E676; font-size:14px; border:1px solid #00E676; padding:2px 6px;'>STRATEGY: MOMENTUM</span>", unsafe_allow_html=True)
    with c_score:
        st.markdown(f"<div style='text-align:right;'><span style='font-size:12px; color:#888;'>AI SCORE</span><br><span style='font-size:36px; color:#00E676; font-weight:bold;'>{row['Score']}</span></div>", unsafe_allow_html=True)

    st.markdown("---")

    # 數據矩陣 (4欄)
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f'<div class="stat-card"><div class="stat-label">建議買入 ENTRY</div><div class="stat-value" style="color:#00E676">${row["Entry"]:.2f}</div></div>', unsafe_allow_html=True)
    k2.markdown(f'<div class="stat-card"><div class="stat-label">止損 STOP</div><div class="stat-value" style="color:#FF1744">${row["Stop"]:.2f}</div></div>', unsafe_allow_html=True)
    k3.markdown(f'<div class="stat-card"><div class="stat-label">DRSI (K/D)</div><div class="stat-value">{row["StochK"]:.0f} / {row["StochD"]:.0f}</div><div class="stat-sub">Stoch RSI Indicator</div></div>', unsafe_allow_html=True)
    k4.markdown(f'<div class="stat-card"><div class="stat-label">盈虧比 R:R</div><div class="stat-value">1 : {row["RR"]:.1f}</div><div class="stat-sub">Risk Reward Ratio</div></div>', unsafe_allow_html=True)

    st.write("")
    
    # 核心分析報告
    c_left, c_right = st.columns([1.2, 2])
    
    with c_left:
        # 顯示買入理由 (Strategy Memo)
        reasons_html = "".join([f"<span class='reason-item'>{r}</span>" for r in row['Reasons']])
        st.markdown(f"""
        <div class="strategy-box">
            <span class="reason-title">⚡ 戰術備忘錄 (Strategy Memo)</span>
            {reasons_html}
            <hr style="border-color:#444;">
            <span style="font-size:12px; color:#aaa;">
            <b>RSI (14):</b> {row['RSI']:.1f} (強弱)<br>
            <b>DRSI Status:</b> {"🟢 黃金交叉" if row['StochK'] > row['StochD'] else "🔴 死亡交叉"}<br>
            <b>建議操作:</b> 掛單買入，嚴守止損。
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # 模擬買入按鈕
        if st.button(f"📥 加入模擬倉 (Buy {row['Symbol']})", use_container_width=True):
            ok, msg = add_to_portfolio(row)
            if ok: st.success(msg)
            else: st.warning(msg)

    with c_right:
        # TradingView 圖表 (加入 Stoch RSI)
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:450px;width:100%">
          <div id="tv_{row['Symbol']}" style="height:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
            "locale": "zh_TW", "toolbar_bg": "#000", "enable_publishing": false, 
            "studies": ["MASimple@tv-basicstudies", "StochasticRSI@tv-basicstudies"],
            "container_id": "tv_{row['Symbol']}"
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=460)

# ==========================================
# 6. 主程式
# ==========================================
inject_css()
init_sim_db()

with st.sidebar:
    st.markdown("### 🦅 ALPHA STATION <span style='color:#00E676; font-size:10px; border:1px solid #00E676; padding:1px 4px;'>PRO</span>", unsafe_allow_html=True)
    mode = st.radio("功能模組", ["⚡ 強勢股掃描 (Pro)", "🤖 模擬交易室", "👀 觀察名單"])
    st.divider()
    
    if mode == "⚡ 強勢股掃描 (Pro)":
        if st.button("🚀 啟動 AI 掃描"):
            with st.spinner("正在分析市場結構..."):
                univ = get_market_universe()
                raw_data = fetch_data(univ)
                
                results = []
                prog = st.progress(0)
                for i, t in enumerate(univ):
                    try:
                        # 處理多層索引
                        d = raw_data[t] if isinstance(raw_data.columns, pd.MultiIndex) else raw_data
                        res = analyze_stock_pro(t, d)
                        if res: results.append(res)
                    except: pass
                    prog.progress((i+1)/len(univ))
                
                prog.empty()
                if results:
                    st.session_state['results'] = pd.DataFrame(results).sort_values('Score', ascending=False)
                    st.toast(f"掃描完成：發現 {len(results)} 個戰術機會", icon="✅")
                else:
                    st.session_state['results'] = pd.DataFrame()
                    st.error("今日無符合高標準的戰術機會。")

# 頁面路由
if mode == "⚡ 強勢股掃描 (Pro)":
    if 'results' in st.session_state and not st.session_state['results'].empty:
        df = st.session_state['results']
        
        c_list, c_main = st.columns([1, 4])
        with c_list:
            st.markdown("### 標的列表")
            sel = st.radio("Select", df['Symbol'].tolist(), label_visibility="collapsed")
        with c_main:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                display_pro_dashboard(row)
    else:
        st.markdown("<div style='text-align:center; padding:50px; color:#666;'><h1>等待指令</h1>請點擊左側 <b>🚀 啟動 AI 掃描</b> 開始分析市場。</div>", unsafe_allow_html=True)

elif mode == "🤖 模擬交易室":
    st.title("🤖 模擬交易室 (Paper Trading)")
    
    col_act, col_stat = st.columns([1, 2])
    with col_act:
        if st.button("🔄 更新行情 & 結算損益", use_container_width=True):
            with st.spinner("正在連接交易所..."):
                msgs, _, _ = check_portfolio_logic()
                if not msgs: st.success("持倉檢查完畢，價格已更新，無觸發事件。")
                else: 
                    for m in msgs: st.toast(m, icon="🔔")
                    st.rerun() # 重新整理以顯示最新數據

    with col_stat:
        log = pd.read_csv(TRADE_LOG_FILE)
        if not log.empty:
            wins = len(log[log['Result']=='WIN'])
            total = len(log)
            win_rate = (wins/total)*100
            pnl = log['Profit_Loss'].sum()
            
            s1, s2, s3 = st.columns(3)
            s1.metric("總勝率 (Win Rate)", f"{win_rate:.1f}%")
            s2.metric("總損益 (Net P&L)", f"${pnl:.2f}", delta=pnl)
            s3.metric("總交易數", f"{total}")

    st.markdown("### 📈 持倉監控")
    pos = pd.read_csv(PORTFOLIO_FILE)
    if not pos.empty:
        st.dataframe(pos, use_container_width=True)
    else:
        st.info("目前無持倉。")

    st.markdown("### 📜 歷史戰績")
    if not log.empty:
        st.dataframe(log.sort_values('Sell_Date', ascending=False), use_container_width=True)

elif mode == "👀 觀察名單":
    st.info("功能維護中 (專注於掃描器優化)")
