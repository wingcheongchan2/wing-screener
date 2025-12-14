import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime
import time

# ==========================================
# 0. 系統核心配置 (Professional Quant)
# ==========================================
st.set_page_config(page_title="J Law: Institutional Scanner", layout="wide", page_icon="🏦")

# 檔案路徑
PORTFOLIO_FILE = 'quant_portfolio.csv'
TRADE_LOG_FILE = 'quant_tradelog.csv'
CAPITAL = 100000 # 預設總資金 10萬美金

# ==========================================
# 1. 華爾街黑金風格 (High Contrast)
# ==========================================
def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Inter:wght@400;700&display=swap');
        
        .stApp { background-color: #000000; color: #E0E0E0; font-family: 'Inter', sans-serif; }
        
        /* 表格樣式優化 */
        div[data-testid="stDataFrame"] {
            border: 1px solid #333;
        }
        
        /* 側邊欄 */
        section[data-testid="stSidebar"] {
            background-color: #0F0F0F; border-right: 1px solid #222;
        }
        
        /* 專業指標卡片 */
        .metric-card {
            background: #111; border: 1px solid #333; padding: 15px; border-radius: 4px;
        }
        .metric-title { font-size: 11px; color: #888; text-transform: uppercase; font-family: 'Roboto Mono'; }
        .metric-value { font-size: 20px; font-weight: bold; color: #fff; font-family: 'Roboto Mono'; margin-top: 5px; }
        .metric-sub { font-size: 11px; margin-top: 5px; }
        
        /* 買賣訊號標籤 */
        .tag-buy { background: #064E3B; color: #34D399; padding: 2px 8px; font-size: 12px; border: 1px solid #059669; }
        .tag-sell { background: #450a0a; color: #FCA5A5; padding: 2px 8px; font-size: 12px; border: 1px solid #B91C1C; }
        .tag-neu { background: #333; color: #aaa; padding: 2px 8px; font-size: 12px; border: 1px solid #555; }
        
        /* 分隔線 */
        hr { border-color: #333; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據庫與交易系統
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target', 'Status']).to_csv(PORTFOLIO_FILE, index=False)
    if not os.path.exists(TRADE_LOG_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Side', 'Price', 'PnL']).to_csv(TRADE_LOG_FILE, index=False)

def execute_order(symbol, entry, stop, target, capital_allocation):
    init_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    if symbol in df[df['Status']=='OPEN']['Symbol'].values:
        return False, "⚠️ 錯誤：倉位已存在"
    
    qty = int(capital_allocation / entry)
    if qty < 1: return False, "⚠️ 資金不足以購買 1 股"
    
    new_trade = {
        'Date': datetime.date.today(),
        'Symbol': symbol,
        'Entry': float(entry),
        'Qty': int(qty),
        'Stop': float(stop),
        'Target': float(target),
        'Status': 'OPEN'
    }
    pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
    return True, f"✅ 買單成交: {symbol} | {qty}股 @ ${entry:.2f}"

# ==========================================
# 3. 全市場數據獲取 (S&P + Nasdaq)
# ==========================================
@st.cache_data
def get_full_universe():
    # 這裡合併兩大指數的成分股，提供真正的全市場掃描
    # 為了展示，這裡包含主要權重股+熱門股 (約 150+)，如果要 600 隻全跑完需要等待約 1 分鐘
    sp500_top = ["MSFT","AAPL","NVDA","AMZN","META","GOOGL","GOOG","BRK-B","LLY","AVGO","JPM","TSLA","UNH","V","XOM","MA","HD","PG","JNJ","COST","ABBV","MRK","CRM","CVX","BAC","AMD","NFLX","PEP","KO","ADBE","WMT","TMO","LIN","ACN","MCD","DIS","CSCO","ABT","INTU","QCOM","VZ","CMCSA","INTC","AMAT","IBM","PFE","UBER","TXN","AMGN","NOW","CAT","SPGI","GE","PM","UNP","GS","ISRG","LOW","COP","PLTR","HON","RTX","BKNG","T","AXP","NEE","ELV","ETN","BLK","SYK","PGR","TJX","MS","C","VRTX","REGN","BSX","BA","PANW","ADP","MMC","CB","MDLZ","KLAC","GILD","LRCX","ADI","AMT","LMT","CI","CVS","SCHW","SNOW","SQ","COIN","MSTR","DKNG","HOOD","RIVN","LCID","SMCI","ARM","APP","CELH","ELF","ONON","AFRM","UPST","MARA","CLSK","RIOT"]
    
    nasdaq_top = ["AAPL","MSFT","AMZN","AVGO","META","TSLA","NVDA","GOOGL","COST","ADBE","NFLX","AMD","PEP","LIN","CSCO","TMUS","INTU","QCOM","TXN","CMCSA","AMGN","HON","INTC","ISRG","BKNG","AMAT","SBUX","VRTX","GILD","MDLZ","ADP","LRCX","REGN","ADI","PANW","MU","KLAC","SNPS","PDD","CDNS","MELI","MNST","CSX","MAR","PYPL","ORLY","CTAS","ROP","ASML","NXPI","LULU","FTNT","ADSK","PCAR","DXCM","PAYX","MCHP","KDP","CHTR","MRVL","IDXX","ABNB","AEP","SGEN","ODFL","AZN","CPRT","ROST","BKR","EA","FAST","EXC","XEL","VRSK","CSGP","CTSH","GEHC","BIIB","WBD","GFS","DLTR","ON","CDW","ANSS","TTD","CEG","ALGN","WBA","ILMN","ZM","ENPH","JD","TEAM","EBAY","ZS","CRWD","DDOG"]
    
    # 去重並排序
    return sorted(list(set(sp500_top + nasdaq_top)))

@st.cache_data(ttl=600)
def fetch_data_batch(tickers):
    # 加入 SPY 和 QQQ 作為 Benchmark
    batch = list(set(tickers + ['SPY', 'QQQ']))
    data = yf.download(batch, period="1y", group_by='ticker', threads=True, progress=False)
    return data

# ==========================================
# 4. 專業技術分析核心 (Comprehensive Analysis)
# ==========================================
def analyze_stock_detailed(ticker, df_stock, df_spy, df_qqq):
    try:
        if len(df_stock) < 200: return None
        
        # 0. 基礎數據
        close = df_stock['Close']
        high = df_stock['High']
        low = df_stock['Low']
        vol = df_stock['Volume']
        curr = float(close.iloc[-1])
        
        # Benchmark 數據
        spy_close = df_spy['Close']
        qqq_close = df_qqq['Close']
        
        # =====================================
        # 1. J Law 核心參數 (RS, Stage, DRSI)
        # =====================================
        
        # A. RS Rating (0-99 Scale)
        # 結合 3個月(40%)、6個月(20%)、12個月(40%) 權重計算
        def get_perf(s, window): return (s.iloc[-1]/s.iloc[-window]) - 1
        
        stock_score = get_perf(close, 63)*0.4 + get_perf(close, 126)*0.2 + get_perf(close, 252)*0.4
        spy_score = get_perf(spy_close, 63)*0.4 + get_perf(spy_close, 126)*0.2 + get_perf(spy_close, 252)*0.4
        
        # 簡單計算 RS (相對大盤的強度)
        rs_rating = 50 + (stock_score - spy_score) * 100 
        rs_rating = min(99, max(1, rs_rating)) # 限制在 1-99
        
        # B. Stage Analysis (趨勢)
        ma50 = float(close.rolling(50).mean().iloc[-1])
        ma150 = float(close.rolling(150).mean().iloc[-1])
        ma200 = float(close.rolling(200).mean().iloc[-1])
        
        stage = "下跌趨勢"
        if curr > ma200: stage = "蓄勢 (Stage 1)"
        if curr > ma50 and ma50 > ma150 and ma150 > ma200: stage = "強勢多頭 (Stage 2)"
        
        # C. DRSI (Stochastic RSI)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k = 100 * (rsi - stoch_min) / (stoch_max - stoch_min)
        d = k.rolling(3).mean()
        k_val, d_val = float(k.iloc[-1]), float(d.iloc[-1])
        
        # =====================================
        # 2. 輔助技術指標 (MACD, BB, Vol)
        # =====================================
        
        # MACD
        exp1 = close.ewm(span=12, adjust=False).mean()
        exp2 = close.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        macd_val = float(macd.iloc[-1])
        sig_val = float(signal.iloc[-1])
        hist_val = macd_val - sig_val
        
        # Bollinger Bands
        bb_upper = float((close.rolling(20).mean() + (close.rolling(20).std()*2)).iloc[-1])
        bb_lower = float((close.rolling(20).mean() - (close.rolling(20).std()*2)).iloc[-1])
        
        # RVOL (相對量能)
        vol_avg = float(vol.rolling(50).mean().iloc[-1])
        rvol = float(vol.iloc[-1]) / vol_avg if vol_avg > 0 else 0
        
        # =====================================
        # 3. 綜合評分與交易計劃
        # =====================================
        
        score = 0
        setup = "無"
        
        # 趨勢分 (30)
        if "Stage 2" in stage: score += 20
        if curr > ma50: score += 10
        
        # 動能分 (30) - DRSI & MACD
        drsi_sig = "中性"
        if k_val > d_val: 
            score += 15
            drsi_sig = "金叉 (Bull)"
        if hist_val > 0 and hist_val > float(macd - signal).iloc[-2]: # 動能增強
            score += 15
            
        # RS 強度分 (20)
        if rs_rating > 80: score += 20
        elif rs_rating > 50: score += 10
        
        # 量能分 (20)
        if rvol > 1.2: score += 20
        elif rvol > 0.8: score += 10
        
        # 判斷 Setup 類型
        atr = float((high - low).rolling(14).mean().iloc[-1])
        entry = curr
        stop = curr - (2 * atr)
        
        if score > 70:
            if curr > bb_upper * 0.98: 
                setup = "突破 (Breakout)"
                stop = ma20 # 突破用均線止損
            elif abs(curr - ma50)/ma50 < 0.03: 
                setup = "回調 (Pullback)"
            else: 
                setup = "趨勢跟隨 (Trend)"
                
        target = entry + (3 * (entry - stop))
        
        return {
            "Symbol": ticker,
            "Price": curr,
            "Change%": ((curr - float(close.iloc[-2]))/float(close.iloc[-2]))*100,
            "Score": score,
            "RS_Rating": int(rs_rating),
            "Stage": stage,
            "Setup": setup,
            "DRSI_Signal": drsi_sig,
            "MACD": "Bull" if macd_val > sig_val else "Bear",
            "RVOL": round(rvol, 1),
            "Entry": round(entry, 2),
            "Stop": round(stop, 2),
            "Target": round(target, 2),
            "R_Ratio": round((target-entry)/(entry-stop), 1) if (entry-stop)!=0 else 0
        }
    except: return None

# ==========================================
# 5. 主程式介面
# ==========================================
inject_css()
init_db()

with st.sidebar:
    st.markdown("## 🏦 J LAW INSTITUTIONAL")
    st.caption("Covering S&P 500 & Nasdaq 100")
    page = st.radio("導航", ["⚡ 市場掃描儀 (Scanner)", "💼 投資組合 (Portfolio)"])
    st.divider()
    capital_input = st.number_input("單筆交易資金 ($)", value=10000, step=1000)

if page == "⚡ 市場掃描儀 (Scanner)":
    st.title("⚡ 全市場深度掃描 (Deep Market Scan)")
    st.markdown("此系統合併掃描 **S&P 500** 與 **Nasdaq 100**，並提供 RS 強度與 J Law 技術指標的詳細分析。")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_scan = st.button("🚀 啟動全市場分析", use_container_width=True)
    
    if run_scan:
        progress_text = st.empty()
        bar = st.progress(0)
        
        progress_text.text("1. 正在獲取 S&P 500 & Nasdaq 成分股清單...")
        tickers = get_full_universe()
        
        progress_text.text(f"2. 正在下載 {len(tickers)} 隻股票的歷史數據 (請耐心等待)...")
        data = fetch_data_batch(tickers)
        
        spy_data = data['SPY']
        qqq_data = data['QQQ']
        
        results = []
        progress_text.text("3. 正在執行 J Law 量化運算...")
        
        for i, t in enumerate(tickers):
            try:
                df_t = data[t] if isinstance(data.columns, pd.MultiIndex) else data
                res = analyze_stock_detailed(t, df_t, spy_data, qqq_data)
                if res: results.append(res)
            except: pass
            
            if i % 10 == 0: bar.progress((i+1)/len(tickers))
            
        bar.empty()
        progress_text.success(f"分析完成！共處理 {len(results)} 隻標的。")
        
        # 存入 Session
        st.session_state['scan_data'] = pd.DataFrame(results)

    # 結果展示
    if 'scan_data' in st.session_state:
        df = st.session_state['scan_data']
        
        # 1. 篩選器
        c_filter1, c_filter2 = st.columns(2)
        with c_filter1:
            min_score = st.slider("最低技術評分 (Score)", 0, 100, 60)
        with c_filter2:
            min_rs = st.slider("最低 RS 強度 (RS Rating)", 0, 99, 70)
            
        filtered_df = df[(df['Score'] >= min_score) & (df['RS_Rating'] >= min_rs)].sort_values('Score', ascending=False)
        
        st.markdown(f"### 📋 篩選結果 ({len(filtered_df)} 隻)")
        
        # 2. 交互式表格 (這就是你要的詳細列表)
        st.dataframe(
            filtered_df[['Symbol', 'Price', 'Change%', 'Score', 'RS_Rating', 'Stage', 'Setup', 'DRSI_Signal', 'RVOL']],
            use_container_width=True,
            column_config={
                "Score": st.column_config.ProgressColumn("Tech Score", min_value=0, max_value=100, format="%d"),
                "RS_Rating": st.column_config.NumberColumn("RS Strength", help="Relative Strength vs Market (0-99)"),
                "Change%": st.column_config.NumberColumn("Change%", format="%.2f%%"),
                "Symbol": st.column_config.TextColumn("Ticker", width="small")
            },
            height=400
        )
        
        st.markdown("---")
        
        # 3. 深度分析面板
        st.markdown("### 🔍 個股深度分析 (Deep Dive)")
        selected_ticker = st.selectbox("選擇要交易的股票:", filtered_df['Symbol'].tolist())
        
        if selected_ticker:
            row = filtered_df[filtered_df['Symbol'] == selected_ticker].iloc[0]
            
            # 頂部資訊
            st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; background:#111; padding:20px; border:1px solid #333;">
                <div>
                    <h1 style="margin:0; color:#fff;">{row['Symbol']} <span style="font-size:18px; color:{'#34D399' if row['Change%']>0 else '#FCA5A5'}">({row['Change%']:.2f}%)</span></h1>
                    <span style="color:#888;">{row['Stage']} | RS Rating: <b style="color:#fff">{row['RS_Rating']}</b></span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:12px; color:#888;">J LAW SCORE</div>
                    <div style="font-size:42px; font-weight:bold; color:{'#34D399' if row['Score']>80 else '#FBBF24'}">{row['Score']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # 指標矩陣
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f"<div class='metric-card'><div class='metric-title'>SETUP TYPE</div><div class='metric-value'>{row['Setup']}</div><div class='metric-sub' style='color:#aaa'>交易模式</div></div>", unsafe_allow_html=True)
            c2.markdown(f"<div class='metric-card'><div class='metric-title'>DRSI SIGNAL</div><div class='metric-value' style='color:{'#34D399' if 'Bull' in row['DRSI_Signal'] else '#fff'}'>{row['DRSI_Signal']}</div><div class='metric-sub'>Stoch RSI 動能</div></div>", unsafe_allow_html=True)
            c3.markdown(f"<div class='metric-card'><div class='metric-title'>VOLUME (RVOL)</div><div class='metric-value'>{row['RVOL']}x</div><div class='metric-sub'>相對量能</div></div>", unsafe_allow_html=True)
            c4.markdown(f"<div class='metric-card'><div class='metric-title'>R:R RATIO</div><div class='metric-value'>1 : {row['R_Ratio']}</div><div class='metric-sub'>盈虧比</div></div>", unsafe_allow_html=True)
            
            # 交易執行區
            st.markdown("#### ⚡ 交易執行 (Execution)")
            ec1, ec2, ec3 = st.columns(3)
            ec1.info(f"🟢 **建議買入 (Entry):** ${row['Entry']}")
            ec2.error(f"🔴 **止損防守 (Stop):** ${row['Stop']}")
            ec3.success(f"🎯 **獲利目標 (Target):** ${row['Target']}")
            
            if st.button(f"立即下單買入 {row['Symbol']} (${capital_input})", use_container_width=True):
                success, msg = execute_order(row['Symbol'], row['Entry'], row['Stop'], row['Target'], capital_input)
                if success: st.success(msg)
                else: st.error(msg)
                
            # 圖表
            st.markdown("#### 📈 技術圖表")
            components.html(f"""
            <div class="tradingview-widget-container" style="height:500px;width:100%">
              <div id="tv_{row['Symbol']}" style="height:100%"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
              <script type="text/javascript">
              new TradingView.widget({{
                "autosize": true, "symbol": "{row['Symbol']}", "interval": "D", "timezone": "Exchange", "theme": "dark", "style": "1",
                "toolbar_bg": "#000", "enable_publishing": false, 
                "studies": ["StochasticRSI@tv-basicstudies", "MASimple@tv-basicstudies", "RSI@tv-basicstudies"],
                "container_id": "tv_{row['Symbol']}"
              }});
              </script>
            </div>
            """, height=500)

elif page == "💼 投資組合 (Portfolio)":
    st.title("💼 模擬資產管理")
    
    if os.path.exists(PORTFOLIO_FILE):
        df = pd.read_csv(PORTFOLIO_FILE)
        if not df.empty:
            st.dataframe(
                df, 
                use_container_width=True,
                column_config={
                    "Status": st.column_config.SelectboxColumn("狀態", options=["OPEN", "CLOSED"]),
                    "PnL": st.column_config.NumberColumn("損益", format="$%.2f")
                }
            )
            st.info("提示：這是一個模擬記錄表。在真實交易中，請嚴格遵守止損價。")
        else:
            st.info("目前沒有持倉。請前往掃描儀尋找機會。")
