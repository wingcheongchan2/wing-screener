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
st.set_page_config(page_title="J Law Wealth Engine", layout="wide", page_icon="💰")

# 檔案設定
PORTFOLIO_FILE = 'jlaw_portfolio.csv'
TRADE_LOG_FILE = 'jlaw_tradelog.csv'
CAPITAL_PER_TRADE = 10000  # 每次交易本金

# ==========================================
# 1. 視覺風格 (J Law 專業黑金版)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');
        
        .stApp { background-color: #080808; color: #f0f0f0; font-family: 'Noto Sans TC', sans-serif; }
        section[data-testid="stSidebar"] { background-color: #000; border-right: 1px solid #333; }
        
        /* 關鍵數據格 */
        .signal-box {
            background: #111; border: 1px solid #444; padding: 15px; border-radius: 6px; text-align: center;
        }
        .signal-label { color: #888; font-size: 12px; margin-bottom: 5px; letter-spacing: 1px; }
        .signal-value { color: #fff; font-size: 24px; font-family: 'JetBrains Mono'; font-weight: bold; }
        
        /* 買賣信號顏色 */
        .bull { color: #00E676 !important; border-color: #00E676 !important; }
        .bear { color: #FF1744 !important; border-color: #FF1744 !important; }
        
        /* 分析報告 */
        .strategy-note {
            background: #1a1a1a; border-left: 5px solid #D4AF37; padding: 15px; font-size: 14px; line-height: 1.6; margin-bottom: 15px;
        }
        
        /* 按鈕 */
        div.stButton > button { background: #222; border: 1px solid #555; color: white; width: 100%; transition: 0.3s; }
        div.stButton > button:hover { border-color: #D4AF37; color: #D4AF37; background: #111; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據庫與模擬器 (自動記錄)
# ==========================================
def init_db():
    # 自動修復 CSV 格式問題
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target']).to_csv(PORTFOLIO_FILE, index=False)
    
    # 檢查並修復交易日誌
    if os.path.exists(TRADE_LOG_FILE):
        try:
            df = pd.read_csv(TRADE_LOG_FILE)
            if 'PnL' not in df.columns: raise ValueError("格式過期")
        except:
            os.remove(TRADE_LOG_FILE)
            pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Exit', 'PnL', 'Result']).to_csv(TRADE_LOG_FILE, index=False)
    else:
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Exit', 'PnL', 'Result']).to_csv(TRADE_LOG_FILE, index=False)

def execute_trade(action, data=None):
    init_db()
    if action == "buy" and data:
        port = pd.read_csv(PORTFOLIO_FILE)
        if data['Symbol'] in port['Symbol'].values: return "⚠️ 已經持有該股票！"
        
        qty = int(CAPITAL_PER_TRADE / data['Entry'])
        new_trade = {
            'Date': datetime.date.today(),
            'Symbol': data['Symbol'],
            'Entry': data['Entry'],
            'Qty': qty,
            'Stop': data['Stop'],
            'Target': data['Target']
        }
        pd.concat([port, pd.DataFrame([new_trade])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
        return f"✅ 交易執行：以 ${data['Entry']:.2f} 買入 {qty} 股 {data['Symbol']}"
    
    if action == "update":
        # 簡單模擬更新價格 (實際應連網)
        port = pd.read_csv(PORTFOLIO_FILE)
        log = pd.read_csv(TRADE_LOG_FILE)
        return port, log

# ==========================================
# 3. J Law 核心策略引擎 (含進場點計算)
# ==========================================
@st.cache_data
def get_focus_list():
    # 這裡放流動性最好的強勢股，保證有野掃
    return ["NVDA", "TSLA", "MSTR", "PLTR", "COIN", "AMD", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "CRWD", "UBER", "ABNB", "DKNG", "MARA", "CLSK", "RIOT", "SOFI", "AI", "HOOD"]

@st.cache_data(ttl=300)
def get_market_data(tickers):
    tickers = list(set(tickers + ['SPY'])) # 加入 SPY 做對比
    return yf.download(tickers, period="1y", group_by='ticker', threads=True, progress=False)

def analyze_jlaw_wealth_logic(ticker, df, spy_df):
    try:
        if len(df) < 200: return None
        
        # 提取基礎數據
        close = df['Close']
        high = df['High']
        low = df['Low']
        curr_price = float(close.iloc[-1])
        
        # 1. 趨勢判斷 (Stage 2)
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        
        trend_score = 0
        if curr_price > ma50: trend_score += 1
        if ma50 > ma200: trend_score += 1
        
        # 2. RS 相對強度 (vs SPY)
        stock_perf = (curr_price / float(close.iloc[-60])) - 1
        spy_perf = (float(spy_df['Close'].iloc[-1]) / float(spy_df['Close'].iloc[-60])) - 1
        rs_rating = "強勢" if stock_perf > spy_perf else "弱勢"
        
        # 3. DRSI (Stoch RSI) - 這是你的關鍵指標
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        
        k_val = float(k.iloc[-1])
        d_val = float(d.iloc[-1])
        
        # 4. 關鍵：進場點計算 (Entry Point Logic)
        # 邏輯：如果多頭強勢，建議在「突破點」或「均線回測點」進場
        # 這裡為了讓你直接能用，我們設定 Entry 為 ATR 保護後的價格
        atr = float((high - low).rolling(14).mean().iloc[-1])
        
        setup_type = ""
        entry_price = 0.0
        stop_price = 0.0
        
        # 策略 A: 均線回調 (Pullback)
        if abs(curr_price - ma20) / ma20 < 0.03 and curr_price > ma20:
            setup_type = "均線回調 (Pullback)"
            entry_price = curr_price # 現價進場
            stop_price = ma20 - (atr * 0.5) # 跌破 MA20 止損
            
        # 策略 B: 強勢突破 (Momentum)
        elif trend_score == 2 and k_val > d_val:
            setup_type = "動能突破 (Momentum)"
            entry_price = curr_price # 確認金叉後進場
            stop_price = curr_price - (2 * atr) # 2ATR 止損
            
        else:
            # 如果不是好機會，還是計算點位，但標記為觀察
            setup_type = "觀察中 (Watch)"
            entry_price = curr_price
            stop_price = curr_price * 0.95
        
        # 計算目標 (3R)
        risk = entry_price - stop_price
        if risk <= 0: risk = curr_price * 0.05 # 防止錯誤
        target_price = entry_price + (risk * 3)
        
        # 總分計算 (0-100)
        score = 0
        if trend_score == 2: score += 40
        if rs_rating == "強勢": score += 30
        if k_val > d_val: score += 20
        if k_val < 20: score += 10 # 超賣加分
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Price": curr_price,
            "Setup": setup_type,
            "Entry": entry_price,
            "Stop": stop_price,
            "Target": target_price,
            "Risk": risk,
            "DRSI_K": k_val,
            "DRSI_D": d_val,
            "RS": rs_rating
        }
    except:
        return None

# ==========================================
# 4. 主程式介面
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.markdown("### 💰 J LAW WEALTH SYSTEM", unsafe_allow_html=True)
    mode = st.radio("系統模式", ["⚡ 智能掃描 (Scanner)", "📈 資產管理 (Portfolio)"])
    st.divider()
    if st.button("🛠️ 系統修復 (Reset)", use_container_width=True):
        if os.path.exists(PORTFOLIO_FILE): os.remove(PORTFOLIO_FILE)
        if os.path.exists(TRADE_LOG_FILE): os.remove(TRADE_LOG_FILE)
        init_db()
        st.success("數據庫已重置")
        st.rerun()

if mode == "⚡ 智能掃描 (Scanner)":
    st.title("⚡ J Law 智能掃描器")
    st.caption("策略邏輯：Stage 2 趨勢 + RS 強度 + DRSI 進場點確認")
    
    if st.button("🚀 開始尋找交易機會", use_container_width=True):
        with st.spinner("AI 正在分析市場結構與計算進場點..."):
            tickers = get_focus_list()
            data = get_market_data(tickers)
            
            if data is None:
                st.error("數據源連接失敗")
            else:
                spy_data = data['SPY']
                results = []
                bar = st.progress(0)
                
                for i, t in enumerate(tickers):
                    try:
                        df_t = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                        res = analyze_jlaw_wealth_logic(t, df_t, spy_data)
                        if res and res['Score'] >= 50: # 只顯示 50 分以上的
                            results.append(res)
                    except: pass
                    bar.progress((i+1)/len(tickers))
                bar.empty()
                
                if results:
                    st.session_state['scan_results'] = pd.DataFrame(results).sort_values('Score', ascending=False)
                    st.success(f"掃描完成！發現 {len(results)} 個潛在機會")
                else:
                    st.warning("目前沒有高分標的，建議空倉觀望。")

    if 'scan_results' in st.session_state:
        df = st.session_state['scan_results']
        
        c1, c2 = st.columns([1, 2.5])
        with c1:
            st.markdown("### 標的列表")
            # 顯示格式: 代碼 (分數)
            sel = st.radio("Select", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x} (Score: {df[df['Symbol']==x]['Score'].values[0]})",
                         label_visibility="collapsed")
        
        with c2:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                
                # Header
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1 style="margin:0; font-size:42px; color:#D4AF37;">{row['Symbol']}</h1>
                    <div style="text-align:right;">
                        <span style="color:#888;">策略評分</span><br>
                        <span style="font-size:30px; font-weight:bold; color:{'#00E676' if row['Score']>70 else '#fff'}">{row['Score']}</span>
                    </div>
                </div>
                <div style="margin-bottom:20px; color:#aaa;">策略形態: <span style="color:#fff; font-weight:bold;">{row['Setup']}</span> | RS強度: {row['RS']}</div>
                """, unsafe_allow_html=True)
                
                # 核心交易數據 (進場/止損/止賺)
                k1, k2, k3, k4 = st.columns(4)
                
                # 根據計算出的點位顯示，如果有金叉，進場點標綠
                k1.markdown(f"""
                <div class="signal-box bull" style="border-width:2px;">
                    <div class="signal-label">建議進場 ENTRY</div>
                    <div class="signal-value">${row['Entry']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                k2.markdown(f"""
                <div class="signal-box bear">
                    <div class="signal-label">止損防守 STOP</div>
                    <div class="signal-value">${row['Stop']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                k3.markdown(f"""
                <div class="signal-box">
                    <div class="signal-label">目標獲利 TARGET</div>
                    <div class="signal-value" style="color:#00E676">${row['Target']:.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                k4.markdown(f"""
                <div class="signal-box">
                    <div class="signal-label">DRSI (K/D)</div>
                    <div class="signal-value">{row['DRSI_K']:.0f} / {row['DRSI_D']:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("")
                
                # J Law 分析邏輯
                st.markdown(f"""
                <div class="strategy-note">
                    <b>🦅 J Law 戰術分析備忘錄：</b><br>
                    1. <b>進場理由：</b> 該股處於 {row['Setup']} 階段，相對強度 (RS) 為 {row['RS']}。<br>
                    2. <b>DRSI 狀態：</b> K值({row['DRSI_K']:.0f}) {"大於" if row['DRSI_K']>row['DRSI_D'] else "小於"} D值({row['DRSI_D']:.0f})，{"動能增強" if row['DRSI_K']>row['DRSI_D'] else "動能減弱"}。<br>
                    3. <b>風控計畫：</b> 買入後潛在虧損控制在每股 ${row['Risk']:.2f}，預期盈虧比 (R:R) 為 1:3。<br>
                </div>
                """, unsafe_allow_html=True)
                
                # 交易按鈕
                if st.button(f"⚡ 立即執行模擬買入 ({row['Symbol']})", use_container_width=True):
                    res = execute_trade("buy", row)
                    st.success(res)
                
                st.divider()
                # 圖表
                components.html(f"""
                <div class="tradingview-widget-container" style="height:400px;width:100%">
                  <div id="tv_{row['Symbol']}" style="height:100%"></div>
                  <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                  <script type="text/javascript">
                  new TradingView.widget({{
                    "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                    "toolbar_bg": "#000", "enable_publishing": false, "hide_top_toolbar": true,
                    "studies": ["StochasticRSI@tv-basicstudies", "MASimple@tv-basicstudies"],
                    "container_id": "tv_{row['Symbol']}"
                  }});
                  </script>
                </div>
                """, height=400)

elif mode == "📈 資產管理 (Portfolio)":
    st.title("📈 資產增值管理")
    
    port, log = execute_trade("update")
    
    # 計算總勝率
    if not log.empty:
        wins = len(log[log['PnL'] > 0])
        total = len(log)
        win_rate = (wins/total*100) if total > 0 else 0
        total_pnl = log['PnL'].sum()
    else:
        win_rate = 0
        total_pnl = 0
        
    m1, m2, m3 = st.columns(3)
    m1.metric("模擬倉總盈虧", f"${total_pnl:.2f}", delta=total_pnl)
    m2.metric("交易勝率", f"{win_rate:.1f}%")
    m3.metric("持倉標的數", len(port))
    
    st.subheader("目前持倉 (Active Positions)")
    if not port.empty:
        st.dataframe(port, use_container_width=True)
        if st.button("🔄 刷新最新價格 (模擬結算)"):
            st.info("功能演示：此處應連接實時數據進行止盈止損檢查。")
    else:
        st.info("目前空倉，請前往掃描器尋找機會。")
        
    st.subheader("交易日誌 (History)")
    if not log.empty:
        st.dataframe(log, use_container_width=True)
