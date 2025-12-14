import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime

# ==========================================
# 0. 系統核心配置 (Nasdaq Edition)
# ==========================================
st.set_page_config(page_title="J Law: Nasdaq Scanner", layout="wide", page_icon="🦅")

# 檔案設定
PORTFOLIO_FILE = 'jlaw_nasdaq_portfolio.csv'
TRADE_LOG_FILE = 'jlaw_nasdaq_log.csv'
CAPITAL_PER_TRADE = 10000

# ==========================================
# 1. 視覺風格 (Tech Blue/Black Theme)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');
        
        .stApp { background-color: #020617; color: #e2e8f0; font-family: 'Noto Sans TC', sans-serif; }
        section[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
        
        /* 霓虹特效框 */
        .neon-box {
            background: rgba(14, 165, 233, 0.1); 
            border: 1px solid #0ea5e9; 
            padding: 15px; 
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(14, 165, 233, 0.2);
            text-align: center;
        }
        .neon-label { color: #94a3b8; font-size: 12px; letter-spacing: 1px; }
        .neon-val { color: #fff; font-size: 24px; font-family: 'JetBrains Mono'; font-weight: bold; }
        
        /* 列表樣式 */
        div[data-testid="stRadio"] > label {
            background: #1e293b; border: 1px solid #334155; margin-bottom: 5px; color: #cbd5e1;
        }
        div[data-testid="stRadio"] > label:hover {
            border-color: #0ea5e9; color: #0ea5e9;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據庫與模擬
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target']).to_csv(PORTFOLIO_FILE, index=False)

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
        return f"✅ 已買入 {data['Symbol']} (Nasdaq)"
    return "OK"

# ==========================================
# 3. 數據源：Nasdaq 100 全成分股
# ==========================================
@st.cache_data
def get_nasdaq_tickers():
    # 這是 Nasdaq 100 的完整列表 (包含科技、生技、高成長)
    # 保證不錯過任何龍頭股
    return [
        "AAPL", "MSFT", "AMZN", "AVGO", "META", "TSLA", "NVDA", "GOOGL", "GOOG", "COST",
        "ADBE", "NFLX", "AMD", "PEP", "LIN", "CSCO", "TMUS", "INTU", "QCOM", "TXN",
        "CMCSA", "AMGN", "HON", "INTC", "ISRG", "BKNG", "AMAT", "SBUX", "VRTX", "GILD",
        "MDLZ", "ADP", "LRCX", "REGN", "ADI", "PANW", "MU", "KLAC", "SNPS", "PDD",
        "CDNS", "MELI", "MNST", "CSX", "MAR", "PYPL", "ORLY", "CTAS", "ROP", "ASML",
        "NXPI", "LULU", "FTNT", "ADSK", "PCAR", "DXCM", "PAYX", "MCHP", "KDP", "CHTR",
        "MRVL", "IDXX", "ABNB", "AEP", "SGEN", "ODFL", "AZN", "CPRT", "ROST", "BKR",
        "EA", "FAST", "EXC", "XEL", "VRSK", "CSGP", "CTSH", "GEHC", "BIIB", "WBD",
        "GFS", "DLTR", "ON", "CDW", "ANSS", "TTD", "CEG", "ALGN", "WBA", "ILMN", 
        "ZM", "LCID", "SIRI", "ENPH", "JD", "TEAM", "EBAY", "ZS", "CRWD", "DDOG",
        "PLTR", "COIN", "MSTR", "SMCI", "ARM", "APP", "HOOD", "AFRM", "UPST"
    ]

@st.cache_data(ttl=600)
def fetch_nasdaq_data(tickers):
    # 加入 QQQ 作為大盤對比 (因為我們是做 Nasdaq)
    syms = list(set(tickers + ['QQQ']))
    data = yf.download(syms, period="1y", group_by='ticker', threads=True, progress=False)
    return data

# ==========================================
# 4. J LAW 核心算法 (針對 Nasdaq 優化)
# ==========================================
def calculate_jlaw_tech_score(ticker, df_stock, df_qqq):
    try:
        if len(df_stock) < 200: return None
        
        # 提取數據
        close = df_stock['Close']
        high = df_stock['High']
        low = df_stock['Low']
        curr = float(close.iloc[-1])
        
        # --- 1. 趨勢強度 (Trend) ---
        ma20 = float(close.rolling(20).mean().iloc[-1])
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        
        is_stage2 = curr > ma200
        trend_status = "震盪"
        if curr > ma50 and ma50 > ma200: trend_status = "強勢多頭"
        elif curr < ma50: trend_status = "回調/弱勢"
        
        # --- 2. RS 相對強度 (vs Nasdaq QQQ) ---
        # 比較 60天 (一季) 漲幅
        stock_ret = (curr / float(close.iloc[-60])) - 1
        qqq_ret = (float(df_qqq['Close'].iloc[-1]) / float(df_qqq['Close'].iloc[-60])) - 1
        
        rs_score = 0
        rs_text = "弱於大盤"
        if stock_ret > qqq_ret: 
            rs_score = 30
            rs_text = "強於納指"
        if stock_ret > qqq_ret * 1.5:
            rs_score = 40
            rs_text = "納指領頭羊"
            
        # --- 3. DRSI (Stochastic RSI) 進場板機 ---
        # 計算 RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        
        # 計算 Stoch RSI
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        
        k_val = float(k.iloc[-1])
        d_val = float(d.iloc[-1])
        
        # --- 評分系統 (總分 100) ---
        score = 0
        reasons = []
        
        # 趨勢 (30分)
        if is_stage2: score += 10
        if trend_status == "強勢多頭": score += 20
        
        # RS (40分) - 科技股最看重強者恆強
        score += rs_score
        
        # DRSI (30分)
        drsi_sig = "無訊號"
        if k_val > d_val:
            score += 20
            drsi_sig = "金叉 (買入)"
            reasons.append("DRSI 金叉")
        elif k_val < 20:
            score += 10
            drsi_sig = "超賣 (準備)"
        
        # 計算 ATR 止損
        atr = float((high - low).rolling(14).mean().iloc[-1])
        stop = curr - (2 * atr)
        if trend_status == "強勢多頭": # 強勢股可以用均線防守
            stop = max(stop, ma20 * 0.98)
            
        target = curr + (3 * (curr - stop))
        
        return {
            "Symbol": ticker,
            "Score": score,
            "Price": curr,
            "Trend": trend_status,
            "RS": rs_text,
            "DRSI_K": k_val,
            "DRSI_D": d_val,
            "Signal": drsi_sig,
            "Entry": curr,
            "Stop": stop,
            "Target": target
        }
    except: return None

# ==========================================
# 5. 主介面
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.markdown("### 🦅 J LAW: NASDAQ 100")
    menu = st.radio("系統", ["⚡ Nasdaq 掃描", "📈 模擬倉"])

if menu == "⚡ Nasdaq 掃描":
    st.title("⚡ J Law 納指動能掃描器")
    st.markdown("針對 **Nasdaq 100** 成分股進行全盤掃描，專注於 **RS 強度** 與 **DRSI**。")
    
    if st.button("🚀 啟動掃描 (Scan Nasdaq)", use_container_width=True):
        status = st.empty()
        status.info("正在獲取 Nasdaq 100 數據...")
        
        tickers = get_nasdaq_tickers()
        data = fetch_nasdaq_data(tickers)
        qqq_data = data['QQQ']
        
        results = []
        bar = st.progress(0)
        
        for i, t in enumerate(tickers):
            try:
                df_t = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                res = calculate_jlaw_tech_score(t, df_t, qqq_data)
                if res: results.append(res)
            except: pass
            bar.progress((i+1)/len(tickers))
        
        bar.empty()
        status.success(f"掃描完成！分析了 {len(results)} 隻納指成分股。")
        st.session_state['nasdaq_res'] = pd.DataFrame(results).sort_values('Score', ascending=False)

    if 'nasdaq_res' in st.session_state:
        df = st.session_state['nasdaq_res']
        
        c1, c2 = st.columns([1, 3])
        with c1:
            st.markdown(f"**結果 ({len(df)})**")
            sel = st.radio("股票列表", df['Symbol'].tolist(), 
                         format_func=lambda x: f"{x} [{df[df['Symbol']==x]['Score'].values[0]}]",
                         label_visibility="collapsed")
            
        with c2:
            if sel:
                row = df[df['Symbol'] == sel].iloc[0]
                
                # Header
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h1 style="margin:0; color:#fff; font-size:48px;">{row['Symbol']}</h1>
                    <div style="text-align:right;">
                        <span style="color:#0ea5e9;">J Law Score</span><br>
                        <span style="font-size:42px; font-weight:bold; color:#fff;">{row['Score']}</span>
                    </div>
                </div>
                <div style="margin-bottom:20px;">
                    <span style="background:#0ea5e9; color:#000; padding:2px 6px; font-weight:bold;">{row['Trend']}</span>
                    <span style="border:1px solid #fff; padding:2px 6px; margin-left:10px;">{row['RS']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # 霓虹數據格
                k1, k2, k3, k4 = st.columns(4)
                k1.markdown(f"<div class='neon-box'><div class='neon-label'>現價 PRICE</div><div class='neon-val'>${row['Price']:.2f}</div></div>", unsafe_allow_html=True)
                k2.markdown(f"<div class='neon-box'><div class='neon-label'>DRSI (K)</div><div class='neon-val' style='color:{'#00E676' if row['DRSI_K']>row['DRSI_D'] else '#fff'}'>{row['DRSI_K']:.0f}</div></div>", unsafe_allow_html=True)
                k3.markdown(f"<div class='neon-box'><div class='neon-label'>止損 STOP</div><div class='neon-val' style='color:#ef4444'>${row['Stop']:.2f}</div></div>", unsafe_allow_html=True)
                k4.markdown(f"<div class='neon-box'><div class='neon-label'>目標 TARGET</div><div class='neon-val' style='color:#00E676'>${row['Target']:.2f}</div></div>", unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 操作建議
                col_act, col_chart = st.columns([1, 1.5])
                with col_act:
                    st.markdown(f"""
                    <div style="background:#0f172a; padding:20px; border-radius:10px; border:1px solid #1e293b;">
                        <h4 style="color:#0ea5e9; margin-top:0;">🦅 J Law 戰術板</h4>
                        <ul style="color:#cbd5e1; padding-left:20px;">
                            <li><b>RS 強度：</b> {row['RS']} (vs QQQ)</li>
                            <li><b>DRSI 訊號：</b> {row['Signal']} (K:{row['DRSI_K']:.0f} / D:{row['DRSI_D']:.0f})</li>
                            <li><b>盈虧比：</b> 1 : 3</li>
                        </ul>
                        <hr style="border-color:#333;">
                        <div style="font-size:12px; color:#64748b;">建議：若 DRSI 金叉且 RS 強勢，為 A+ 級買點。</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"⚡ 模擬買入 {row['Symbol']}", use_container_width=True):
                        msg = execute_trade("buy", row)
                        st.success(msg)
                        
                with col_chart:
                    components.html(f"""
                    <div class="tradingview-widget-container" style="height:450px;width:100%">
                      <div id="tv_{row['Symbol']}" style="height:100%"></div>
                      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
                      <script type="text/javascript">
                      new TradingView.widget({{
                        "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                        "toolbar_bg": "#000", "enable_publishing": false, 
                        "studies": ["StochasticRSI@tv-basicstudies", "MASimple@tv-basicstudies"],
                        "container_id": "tv_{row['Symbol']}"
                      }});
                      </script>
                    </div>
                    """, height=450)

elif menu == "📈 模擬倉":
    st.title("📈 Nasdaq 模擬投資組合")
    if os.path.exists(PORTFOLIO_FILE):
        df = pd.read_csv(PORTFOLIO_FILE)
        if not df.empty:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("目前無持倉。")
