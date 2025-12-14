import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime

# ==========================================
# 0. 系統核心配置
# ==========================================
st.set_page_config(page_title="J Law Alpha Station: Stable", layout="wide", page_icon="🦅")

# 檔案路徑
PORTFOLIO_FILE = 'sim_portfolio_v2.csv'
TRADE_LOG_FILE = 'sim_trade_log_v2.csv' # 改名以避免讀取舊版壞檔
CAPITAL_PER_TRADE = 10000

# ==========================================
# 1. 視覺風格 (Professional Dark)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        .stApp { background-color: #000000; color: #e0e0e0; font-family: 'Roboto Condensed', sans-serif; }
        section[data-testid="stSidebar"] { background-color: #0a0a0a; border-right: 1px solid #333; }
        
        /* 數據卡片 */
        .metric-box {
            background: #111; border: 1px solid #333; padding: 15px; border-radius: 4px;
        }
        .metric-label { font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 24px; color: #fff; font-family: 'JetBrains Mono'; font-weight: bold; }
        
        /* J Law 報告樣式 */
        .report-box {
            background: #0f0f0f; border-left: 4px solid #E53935; padding: 15px; margin-top: 10px;
        }
        .score-badge {
            background: #E53935; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; font-family: 'JetBrains Mono';
        }
        
        /* 按鈕優化 */
        div.stButton > button { background: #222; color: #fff; border: 1px solid #444; width: 100%; }
        div.stButton > button:hover { border-color: #E53935; color: #E53935; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據源與掃描邏輯 (修復版)
# ==========================================
@st.cache_data
def get_universe():
    # 核心強勢股名單 (包含 Mag 7, Semi, Crypto, Growth)
    return [
        "NVDA", "TSLA", "MSTR", "PLTR", "COIN", "SMCI", "AMD", "AAPL", "MSFT", "AMZN", 
        "GOOGL", "META", "AVGO", "CRWD", "UBER", "ABNB", "DKNG", "MARA", "CLSK", "RIOT", 
        "SOFI", "AI", "ARM", "MU", "QCOM", "TSM", "HOOD", "NET", "PANW", "SNOW", "ONON", 
        "ELF", "CELH", "APP", "CVNA", "UPST"
    ]

@st.cache_data(ttl=600)
def fetch_data(tickers):
    # 下載數據，加入 SPY 用於對比 RS
    tickers = list(set(tickers + ['SPY']))
    try:
        data = yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)
        return data
    except Exception as e:
        return None

def calculate_technical_score(ticker, df, spy_df):
    try:
        if len(df) < 200: return None
        
        # 提取數據
        close = df['Close']
        high = df['High']
        ma50 = close.rolling(50).mean().iloc[-1]
        ma200 = close.rolling(200).mean().iloc[-1]
        vol = df['Volume']
        curr_price = close.iloc[-1]
        
        # --- 評分邏輯 (總分 100) ---
        score = 0
        reasons = []
        
        # 1. 趨勢 (Trend) - 佔 40分
        if curr_price > ma200:
            score += 10
            if curr_price > ma50:
                score += 15
                if ma50 > ma200:
                    score += 15
                    reasons.append("📈 **多頭排列 (Stage 2)**: 價格 > 50MA > 200MA")
        
        # 2. 相對強度 (RS vs SPY) - 佔 30分
        stock_ret = (close.iloc[-1] / close.iloc[-63]) - 1
        spy_ret = (spy_df['Close'].iloc[-1] / spy_df['Close'].iloc[-63]) - 1
        if stock_ret > spy_ret:
            score += 20
            reasons.append(f"💪 **相對強勢 (RS)**: 跑贏大盤 (股 {stock_ret*100:.1f}% vs SPY {spy_ret*100:.1f}%)")
            if stock_ret > spy_ret * 2:
                score += 10
                reasons.append("🔥 **RS 爆發**: 強度是大盤兩倍以上")

        # 3. DRSI / 動能 - 佔 30分
        # 計算 RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        # 計算 Stoch RSI
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        
        k_val = k.iloc[-1]
        d_val = d.iloc[-1]
        
        if k_val > d_val:
            score += 15
            reasons.append(f"⚡ **DRSI 黃金交叉**: K({k_val:.0f}) > D({d_val:.0f})")
        if 40 <= rsi.iloc[-1] <= 70:
            score += 15 # RSI 健康區間
            
        # 4. 量能加分
        vol_ma = vol.rolling(50).mean().iloc[-1]
        if vol.iloc[-1] > vol_ma * 1.2:
            score += 5
            reasons.append("📊 **放量**: 成交量大於均量 1.2x")

        # 交易參數
        atr = (high - df['Low']).rolling(14).mean().iloc[-1]
        stop = curr_price - (2 * atr)
        target = curr_price + (3 * (curr_price - stop))
        
        # 只要超過 40 分就顯示 (避免零結果)，按分數排序
        if score < 40: return None
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Price": curr_price,
            "Entry": curr_price,
            "Stop": stop,
            "Target": target,
            "K": k_val, "D": d_val,
            "Reasons": reasons
        }
        
    except Exception:
        return None

# ==========================================
# 3. 模擬器與資料庫管理 (自動修復版)
# ==========================================
def init_db():
    # 強制檢查欄位，如果欄位不對，直接重建，防止 KeyError
    expected_cols = ['Date', 'Symbol', 'Profit_Loss', 'Result']
    
    # 檢查 Trade Log
    if os.path.exists(TRADE_LOG_FILE):
        try:
            df = pd.read_csv(TRADE_LOG_FILE)
            if 'Profit_Loss' not in df.columns:
                # 舊版檔案，刪除重建
                os.remove(TRADE_LOG_FILE)
                pd.DataFrame(columns=expected_cols).to_csv(TRADE_LOG_FILE, index=False)
        except:
            os.remove(TRADE_LOG_FILE)
            pd.DataFrame(columns=expected_cols).to_csv(TRADE_LOG_FILE, index=False)
    else:
        pd.DataFrame(columns=expected_cols).to_csv(TRADE_LOG_FILE, index=False)

    # 檢查 Portfolio
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target']).to_csv(PORTFOLIO_FILE, index=False)

def portfolio_action(action, data=None):
    init_db() # 每次操作前先檢查數據庫健康度
    
    if action == "add" and data:
        df = pd.read_csv(PORTFOLIO_FILE)
        if data['Symbol'] in df['Symbol'].values: return "⚠️ 已在持倉中"
        
        qty = int(CAPITAL_PER_TRADE / data['Price'])
        new_row = {
            'Date': datetime.date.today(),
            'Symbol': data['Symbol'],
            'Entry': data['Price'],
            'Qty': qty,
            'Stop': data['Stop'],
            'Target': data['Target']
        }
        pd.concat([df, pd.DataFrame([new_row])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
        return f"✅ 成功買入 {qty} 股 {data['Symbol']}"

    if action == "update":
        # 這裡簡單模擬更新，計算損益
        pos = pd.read_csv(PORTFOLIO_FILE)
        log = pd.read_csv(TRADE_LOG_FILE)
        return pos, log

# ==========================================
# 4. 主介面邏輯
# ==========================================
inject_css()
init_db() # 啟動時自動修復

with st.sidebar:
    st.markdown("### 🦅 J LAW STATION <span style='color:#E53935; font-size:10px;'>STABLE</span>", unsafe_allow_html=True)
    menu = st.radio("功能", ["⚡ 掃描器 (Scanner)", "🤖 模擬器 (Simulator)"])
    
    st.markdown("---")
    if st.button("🗑️ 重置所有數據 (Fix Error)", use_container_width=True):
        if os.path.exists(PORTFOLIO_FILE): os.remove(PORTFOLIO_FILE)
        if os.path.exists(TRADE_LOG_FILE): os.remove(TRADE_LOG_FILE)
        init_db()
        st.success("系統已重置，錯誤已修復。")
        st.rerun()

if menu == "⚡ 掃描器 (Scanner)":
    st.title("⚡ J Law 動能掃描")
    
    if st.button("🚀 啟動掃描 (Start Scan)", use_container_width=True):
        with st.spinner("正在下載華爾街數據 & 分析中 (約需 10-15 秒)..."):
            tickers = get_universe()
            data = fetch_data(tickers)
            
            if data is None or data.empty:
                st.error("無法連接數據源 (Yahoo Finance API Error)，請稍後再試。")
            else:
                spy_data = data['SPY']
                results = []
                
                # 處理進度條
                bar = st.progress(0)
                for i, t in enumerate(tickers):
                    try:
                        df_t = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                        res = calculate_technical_score(t, df_t, spy_data)
                        if res: results.append(res)
                    except: pass
                    bar.progress((i+1)/len(tickers))
                bar.empty()
                
                if results:
                    st.session_state['results'] = pd.DataFrame(results).sort_values('Score', ascending=False)
                    st.toast(f"掃描完成！發現 {len(results)} 個機會", icon="✅")
                else:
                    st.warning("無股票超過 40 分。這代表市場極度疲弱，建議空倉觀望。")

    # 顯示結果
    if 'results' in st.session_state and not st.session_state['results'].empty:
        df = st.session_state['results']
        
        # 佈局：左側列表，右側詳情
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"**結果列表 ({len(df)})**")
            # 格式化顯示： 代碼 (分數)
            options = [f"{r['Symbol']} ({r['Score']})" for _, r in df.iterrows()]
            # 建立映射方便查找
            opt_map = {f"{r['Symbol']} ({r['Score']})": r['Symbol'] for _, r in df.iterrows()}
            
            sel_opt = st.radio("選擇股票", options, label_visibility="collapsed")
            sel_sym = opt_map[sel_opt]
            
        with c2:
            row = df[df['Symbol'] == sel_sym].iloc[0]
            
            # 標題區
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:10px;">
                <div>
                    <h1 style="margin:0; color:#fff;">{row['Symbol']}</h1>
                    <span style="color:#888;">現價: ${row['Price']:.2f}</span>
                </div>
                <div>
                    <span class="score-badge">SCORE: {row['Score']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 數據區
            k1, k2, k3, k4 = st.columns(4)
            k1.markdown(f"<div class='metric-box'><div class='metric-label'>目標 Target</div><div class='metric-value' style='color:#00E676'>${row['Target']:.2f}</div></div>", unsafe_allow_html=True)
            k2.markdown(f"<div class='metric-box'><div class='metric-label'>止損 Stop</div><div class='metric-value' style='color:#FF1744'>${row['Stop']:.2f}</div></div>", unsafe_allow_html=True)
            k3.markdown(f"<div class='metric-box'><div class='metric-label'>DRSI (K)</div><div class='metric-value'>{row['K']:.0f}</div></div>", unsafe_allow_html=True)
            k4.markdown(f"<div class='metric-box'><div class='metric-label'>DRSI (D)</div><div class='metric-value'>{row['D']:.0f}</div></div>", unsafe_allow_html=True)
            
            # 分析與操作
            c_txt, c_cht = st.columns([1, 1.5])
            with c_txt:
                reasons_html = "".join([f"<li>{r}</li>" for r in row['Reasons']])
                st.markdown(f"""
                <div class="report-box">
                    <div style="color:#E53935; font-weight:bold; margin-bottom:5px;">⚡ J Law 戰術分析</div>
                    <ul style="padding-left:20px; color:#ddd; margin:0;">
                        {reasons_html}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                if st.button(f"📥 模擬買入 {row['Symbol']}", use_container_width=True):
                    msg = portfolio_action("add", row)
                    st.success(msg)
            
            with c_cht:
                # TradingView 圖表
                components.html(f"""
                <div class="tradingview-widget-container" style="height:400px;width:100%">
                  <div id="tv_{row['Symbol']}" style="height:100%"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                    "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                    "toolbar_bg": "#000", "enable_publishing": false, "hide_top_toolbar": true,
                    "studies": ["StochasticRSI@tv-basicstudies"],
                    "container_id": "tv_{row['Symbol']}"
                  }});
                  </script>
                </div>
                """, height=400)

elif menu == "🤖 模擬器 (Simulator)":
    st.title("🤖 交易模擬器")
    
    pos, log = portfolio_action("update")
    
    # 統計數據 (防止 crash)
    try:
        total_pnl = log['Profit_Loss'].sum() if not log.empty else 0.0
        wins = len(log[log['Result'] == 'WIN'])
        total = len(log)
        win_rate = (wins / total * 100) if total > 0 else 0
    except KeyError:
        st.error("數據格式錯誤，請點擊側邊欄的「重置所有數據」按鈕。")
        st.stop()
    
    # 儀表板
    m1, m2, m3 = st.columns(3)
    m1.metric("總盈虧 (P&L)", f"${total_pnl:.2f}", delta=total_pnl)
    m2.metric("勝率 (Win Rate)", f"{win_rate:.1f}%")
    m3.metric("總交易數", f"{total}")
    
    st.subheader("持倉中")
    if not pos.empty:
        st.dataframe(pos, use_container_width=True)
    else:
        st.info("目前無持倉。")
        
    st.subheader("歷史交易")
    if not log.empty:
        st.dataframe(log, use_container_width=True)
