import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import os
import datetime

# ==========================================
# 0. 系統核心配置 (System Config)
# ==========================================
st.set_page_config(
    page_title="J Law Alpha Hunter Pro",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

PORTFOLIO_FILE = 'auto_portfolio.csv'

# ==========================================
# 1. 專業級金融終端深色主題 (Institutional CSS)
# ==========================================
def inject_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {
            background-color: #0B0E14;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
        }
        
        section[data-testid="stSidebar"] {
            background-color: #121824;
            border-right: 1px solid #1E293B;
        }
        
        .metric-card {
            background: #151D2E;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            transition: all 0.2s ease;
        }
        .metric-card:hover {
            border-color: #38BDF8;
            box-shadow: 0 4px 12px rgba(56, 189, 248, 0.08);
        }
        
        .card-diamond {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid #06B6D4;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
            position: relative;
        }
        
        .card-gold {
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.1) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 1px solid #EAB308;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
        }
        
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
            margin-right: 6px;
        }
        .badge-diamond { background: rgba(6, 182, 212, 0.2); color: #22D3EE; border: 1px solid #06B6D4; }
        .badge-gold { background: rgba(234, 179, 8, 0.2); color: #FACC15; border: 1px solid #EAB308; }
        .badge-silver { background: rgba(148, 163, 184, 0.15); color: #94A3B8; border: 1px solid #475569; }
        .badge-green { background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }
        .badge-red { background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }
        .badge-cyan { background: rgba(14, 165, 233, 0.2); color: #38BDF8; border: 1px solid #0284C7; }

        .plan-box {
            background: #0D131F;
            border: 1px solid #1E293B;
            border-left: 4px solid #10B981;
            border-radius: 6px;
            padding: 14px;
            margin-top: 12px;
            font-family: 'JetBrains Mono', monospace;
        }

        .market-banner {
            padding: 12px 18px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 持倉資料庫 (Portfolio Management)
# ==========================================
def init_db():
    if not os.path.exists(PORTFOLIO_FILE):
        pd.DataFrame(columns=['Date', 'Symbol', 'Entry', 'Qty', 'Stop', 'Target_2R', 'Target_3R', 'Risk_Amount', 'Status']).to_csv(PORTFOLIO_FILE, index=False)

def execute_trade(symbol, entry, stop, target_2r, target_3r, qty, risk_amount):
    init_db()
    df = pd.read_csv(PORTFOLIO_FILE)
    if not df.empty and symbol in df[df['Status'] == 'OPEN']['Symbol'].values:
        return False, f"⚠️ 已持有未平倉的 {symbol}"
    
    new_trade = {
        'Date': datetime.date.today().strftime('%Y-%m-%d'),
        'Symbol': symbol,
        'Entry': round(entry, 2),
        'Qty': int(qty),
        'Stop': round(stop, 2),
        'Target_2R': round(target_2r, 2),
        'Target_3R': round(target_3r, 2),
        'Risk_Amount': round(risk_amount, 2),
        'Status': 'OPEN'
    }
    pd.concat([df, pd.DataFrame([new_trade])], ignore_index=True).to_csv(PORTFOLIO_FILE, index=False)
    return True, f"✅ 已按風控建立 {symbol} 倉位: {qty} 股 (承受風險: ${risk_amount:.2f})"

# ==========================================
# 3. 核心觀察股票池 (Watchlist Universes)
# ==========================================
def get_universe(universe_type):
    if universe_type == "J Law 核心動能觀察池 (精選 50 隻)":
        return [
            "NVDA", "TSLA", "PLTR", "MSTR", "COIN", "AMD", "META", "AMZN", "MSFT", "GOOGL",
            "AAPL", "AVGO", "ARM", "MU", "CRWD", "PANW", "NET", "SNOW", "DDOG", "SMCI",
            "UBER", "ABNB", "HOOD", "APP", "CVNA", "CELH", "ONON", "DKNG", "SHOP", "SE",
            "SOFI", "AFRM", "UPST", "TTD", "MELI", "ISRG", "LRCX", "KLAC", "ASML", "TSM",
            "CEG", "VST", "BE", "NOW", "AXP", "GS", "LLY", "COST", "NFLX", "QCOM"
        ]
    elif universe_type == "S&P 500 & Nasdaq 100 高流動性 (100 隻)":
        return [
            "NVDA", "TSLA", "MSTR", "COIN", "PLTR", "SMCI", "AMD", "AAPL", "MSFT", "AMZN", 
            "GOOGL", "META", "AVGO", "CRWD", "UBER", "ABNB", "DKNG", "MARA", "CLSK", "RIOT", 
            "SOFI", "ARM", "MU", "QCOM", "TSM", "HOOD", "NET", "PANW", "SNOW", "ONON", 
            "APP", "CVNA", "UPST", "JPM", "V", "LLY", "NFLX", "COST", "ADBE", "INTU", 
            "TXN", "AMGN", "ISRG", "BKNG", "LRCX", "REGN", "KLAC", "SNPS", "CDNS", "MELI", 
            "ORLY", "ASML", "FTNT", "DXCM", "MRVL", "ROST", "FAST", "TTD", "CEG", "ZM", 
            "DDOG", "SQ", "RIVN", "AFRM", "GILD", "MRK", "ABBV", "JNJ", "PG", "HD", 
            "MA", "UNH", "XOM", "CVX", "BAC", "WMT", "KO", "MCD", "DIS", "CAT", 
            "GE", "GS", "BA", "RTX", "HON", "IBM", "DE", "LIN", "PM", "NKE",
            "TMO", "MDT", "ABT", "BMY", "DHR", "LOW", "SCHW", "BLK", "SPGI", "NOW"
        ]
    else:
        return ["NVDA", "TSLA", "PLTR", "AMD", "META", "AMZN", "MSFT", "GOOGL", "AAPL", "AVGO"]

# ==========================================
# 4. 數據獲取與多層解析 (Data Engine)
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_market_and_stocks(tickers):
    benchmark_symbols = ['SPY', 'QQQ']
    all_needed = list(set(tickers + benchmark_symbols))
    
    try:
        raw_data = yf.download(all_needed, period="1y", interval="1d", progress=False, group_by='ticker', threads=True)
    except Exception:
        return None, None, None

    if raw_data is None or raw_data.empty:
        return None, None, None

    def extract_symbol_df(data, sym):
        try:
            if isinstance(data.columns, pd.MultiIndex):
                if sym in data.columns.levels[0]:
                    df = data[sym].copy()
                elif sym in data.columns.levels:
                    df = data.xs(sym, axis=1, level=1).copy()
                else:
                    return None
            else:
                df = data.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception:
            return None

    df_spy = extract_symbol_df(raw_data, 'SPY')
    df_qqq = extract_symbol_df(raw_data, 'QQQ')
    
    stock_dict = {}
    for sym in tickers:
        df_sym = extract_symbol_df(raw_data, sym)
        if df_sym is not None and len(df_sym) >= 150:
            stock_dict[sym] = df_sym

    return stock_dict, df_spy, df_qqq

# ==========================================
# 5. 大市環境分析器 (Market Regime)
# ==========================================
def analyze_market_regime(df_spy, df_qqq):
    if df_spy is None or df_qqq is None or len(df_spy) < 200:
        return {
            "status": "NEUTRAL",
            "title": "大市數據不足",
            "desc": "無法獲取完整的 SPY/QQQ 200日線數據，請謹慎操作。",
            "color": "#64748B",
            "allow_trades": True
        }
    
    def get_market_health(df):
        c = df['Close']
        curr = c.iloc[-1]
        ema20 = c.ewm(span=20, adjust=False).mean().iloc[-1]
        sma50 = c.rolling(50).mean().iloc[-1]
        sma200 = c.rolling(200).mean().iloc[-1]
        is_bull = (curr > sma50) and (sma50 > sma200)
        is_above_20 = curr > ema20
        return is_bull, is_above_20, curr, sma50

    spy_bull, spy_20, spy_c, spy_ma50 = get_market_health(df_spy)
    qqq_bull, qqq_20, qqq_c, qqq_ma50 = get_market_health(df_qqq)

    if spy_bull and qqq_bull:
        if spy_20 and qqq_20:
            return {
                "status": "STRONG_BULL",
                "title": "🟢 大市處於【強勢多頭】格局 (Stage 2 Uptrend)",
                "desc": "標普 SPY 與納指 QQQ 均站穩 20 EMA 與 50 SMA 之上。多頭勝率最高，可積極捕捉 Diamond 級別突破與回踩買點。",
                "color": "#10B981",
                "bg": "rgba(16, 185, 129, 0.1)",
                "allow_trades": True
            }
        else:
            return {
                "status": "PULLBACK",
                "title": "🟡 大市處於【健康回調 / 震盪期】(Pullback Mode)",
                "desc": "大盤維持中長線多頭，但短線跌破 20 EMA。適合佈局回踩 20 EMA / VCP 收窄股，慎防追高，嚴格控制倉位。",
                "color": "#F59E0B",
                "bg": "rgba(245, 158, 11, 0.1)",
                "allow_trades": True
            }
    else:
        return {
            "status": "BEAR_CORRECTION",
            "title": "🔴 大市處於【調整 / 空頭防守期】(Correction / Defense)",
            "desc": "大盤主要指數已跌破 50 日均線。根據 J Law 紀律：8 成股票隨大盤下挫，建議保留現金，暫停新開多單。",
            "color": "#EF4444",
            "bg": "rgba(239, 68, 68, 0.1)",
            "allow_trades": False
        }

# ==========================================
# 6. J Law 7 大選股系統演算法 (Institutional Alpha)
# ==========================================
def calculate_stock_alpha(ticker, df_stock, df_spy, df_qqq):
    try:
        c = df_stock['Close']
        h = df_stock['High']
        l = df_stock['Low']
        v = df_stock['Volume']
        
        curr_price = float(c.iloc[-1])
        prev_price = float(c.iloc[-2])
        daily_change = ((curr_price - prev_price) / prev_price) * 100

        ema20 = c.ewm(span=20, adjust=False).mean()
        sma50 = c.rolling(50).mean()
        sma150 = c.rolling(150).mean() if len(c) >= 150 else sma50
        sma200 = c.rolling(200).mean() if len(c) >= 200 else sma150

        c_now = curr_price
        ema20_now = float(ema20.iloc[-1])
        sma50_now = float(sma50.iloc[-1])
        sma150_now = float(sma150.iloc[-1])
        sma200_now = float(sma200.iloc[-1])
        sma200_20d_ago = float(sma200.iloc[-20]) if len(c) >= 220 else sma200_now

        rolling_252 = min(len(c), 252)
        h52 = float(h.iloc[-rolling_252:].max())
        l52 = float(l.iloc[-rolling_252:].min())
        dist_to_h52 = ((c_now - h52) / h52) * 100
        dist_from_l52 = ((c_now - l52) / l52) * 100

        stage2_score = 0
        stage2_passed = False
        reasons = []

        cond1 = c_now > sma50_now
        cond2 = sma50_now > sma150_now and sma150_now > sma200_now
        cond3 = sma200_now >= sma200_20d_ago
        cond4 = dist_to_h52 >= -25.0
        cond5 = dist_from_l52 >= 25.0

        if cond1 and cond2:
            stage2_score += 15
        elif cond1:
            stage2_score += 8

        if cond3:
            stage2_score += 5
        if cond4 and cond5:
            stage2_score += 5

        if cond1 and cond2 and cond3 and cond4:
            stage2_passed = True
            reasons.append("Stage 2 多頭排列")

        def calc_perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        p3m = calc_perf(c, 63)
        p6m = calc_perf(c, 126)
        p12m = calc_perf(c, min(252, len(c)-1))
        weighted_perf = (0.4 * p3m) + (0.3 * p6m) + (0.3 * p12m)

        spy_p3m = calc_perf(df_spy['Close'], 63)
        spy_p6m = calc_perf(df_spy['Close'], 126)
        spy_p12m = calc_perf(df_spy['Close'], 252)
        spy_weighted = (0.4 * spy_p3m) + (0.3 * spy_p6m) + (0.3 * spy_p12m)

        rs_excess = (weighted_perf - spy_weighted) * 100
        rs_raw_score = 50 + (rs_excess * 1.5)
        rs_rating = int(np.clip(rs_raw_score, 1, 99))

        rs_points = 0
        if rs_rating >= 85:
            rs_points = 25
            reasons.append(f"強勢領頭羊 (RS {rs_rating})")
        elif rs_rating >= 70:
            rs_points = 18
            reasons.append(f"優於大盤 (RS {rs_rating})")
        elif rs_rating >= 50:
            rs_points = 10

        tr1 = h - l
        tr2 = (h - c.shift(1)).abs()
        tr3 = (l - c.shift(1)).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])

        vcp_points = 0
        atr_ratio = atr14 / (atr50 if atr50 > 0 else 1)
        if atr_ratio <= 0.8:
            vcp_points += 10
            reasons.append("VCP 波動收窄")
        elif atr_ratio <= 0.95:
            vcp_points += 5

        recent_std = float(c.iloc[-5:].std() / c_now)
        if recent_std < 0.02:
            vcp_points += 5
            reasons.append("緊密收市 (Tight Closes)")

        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_min = rsi.rolling(14).min()
        stoch_max = rsi.rolling(14).max()
        k_series = 100 * (rsi - stoch_min) / ((stoch_max - stoch_min).replace(0, 1e-9))
        d_series = k_series.rolling(3).mean()

        k_val = float(k_series.iloc[-1])
        d_val = float(d_series.iloc[-1])
        prev_k = float(k_series.iloc[-2])
        prev_d = float(d_series.iloc[-2])

        drsi_points = 0
        drsi_status = "中性"
        if prev_k <= prev_d and k_val > d_val:
            if k_val < 35:
                drsi_points += 15
                drsi_status = "超賣金叉 (買點成立)"
                reasons.append("DRSI 超賣金叉")
            else:
                drsi_points += 12
                drsi_status = "多頭金叉 (買點成立)"
                reasons.append("DRSI 多頭金叉")
        elif k_val > d_val and k_val > 50:
            drsi_points += 8
            drsi_status = "多頭維持"
        elif k_val < 25:
            drsi_points += 6
            drsi_status = "超賣醞釀"

        ema_points = 0
        dist_to_ema20 = ((c_now - ema20_now) / ema20_now) * 100
        if 0 <= dist_to_ema20 <= 2.5:
            ema_points += 10
            reasons.append("回踩 20 EMA 最佳買區")
        elif -2.0 <= dist_to_ema20 < 0:
            ema_points += 6
            reasons.append("測試 20 EMA 支撐")
        elif 2.5 < dist_to_ema20 <= 6.0:
            ema_points += 5

        vol_points = 0
        vol_50ma = float(v.rolling(50).mean().iloc[-1])
        curr_vol = float(v.iloc[-1])
        rvol = curr_vol / (vol_50ma if vol_50ma > 0 else 1)

        if daily_change > 0 and rvol >= 1.4:
            vol_points += 10
            reasons.append(f"爆量突破 ({rvol:.1f}x)")
        elif rvol < 0.75 and abs(daily_change) < 1.5:
            vol_points += 7
            reasons.append("量能乾涸蓄勢 (VDU)")
        elif rvol >= 1.0:
            vol_points += 4

        total_score = stage2_score + rs_points + vcp_points + drsi_points + ema_points + vol_points
        total_score = int(np.clip(total_score, 0, 100))

        if total_score >= 82 and stage2_passed:
            rank = "Diamond"
        elif total_score >= 68:
            rank = "Gold"
        elif total_score >= 50:
            rank = "Silver"
        else:
            rank = "Bronze"

        entry_price = c_now
        atr_stop = entry_price - (1.5 * atr14)
        ema_stop = ema20_now * 0.985
        stop_price = max(atr_stop, ema_stop)
        max_stop = entry_price * 0.92
        min_stop = entry_price * 0.97
        stop_price = min(max(stop_price, max_stop), min_stop)

        risk_per_share = entry_price - stop_price
        target_2r = entry_price + (2.0 * risk_per_share)
        target_3r = entry_price + (3.0 * risk_per_share)
        stop_pct = ((stop_price - entry_price) / entry_price) * 100

        return {
            "Symbol": ticker,
            "Rank": rank,
            "Score": total_score,
            "Price": curr_price,
            "Change": daily_change,
            "RS": rs_rating,
            "Stage2": "✅ 是" if stage2_passed else "❌ 否",
            "DRSI_K": round(k_val, 1),
            "DRSI_D": round(d_val, 1),
            "DRSI_Status": drsi_status,
            "RVOL": round(rvol, 2),
            "EMA20": round(ema20_now, 2),
            "Dist_20EMA": round(dist_to_ema20, 2),
            "Dist_52H": round(dist_to_h52, 1),
            "ATR": round(atr14, 2),
            "Entry": round(entry_price, 2),
            "Stop": round(stop_price, 2),
            "Stop_Pct": round(stop_pct, 2),
            "Target_2R": round(target_2r, 2),
            "Target_3R": round(target_3r, 2),
            "Reasons": reasons,
            "Raw_Data": df_stock
        }
    except Exception:
        return None

# ==========================================
# 7. 側邊欄控制面板 (Sidebar Controls)
# ==========================================
inject_custom_css()
init_db()

with st.sidebar:
    st.markdown("## 🦅 J LAW ALPHA HUNTER")
    st.caption("Institutional Swing Trading Terminal")
    st.markdown("---")

    st.markdown("### 1. 核心資金與風控設定")
    account_capital = st.number_input("總賬戶資產 ($)", min_value=1000, max_value=10000000, value=50000, step=5000)
    risk_pct = st.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=2.5, value=1.0, step=0.1, help="J Law 嚴格紀律：單筆虧損金額不超過總資產的 1%~2%")
    max_pos_cap = st.slider("單一持倉上限 (% 總資金)", min_value=10, max_value=35, value=25, step=5)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    st.markdown(f"""
    <div style="background:#151D2E; border:1px solid #1E293B; border-radius:6px; padding:10px; font-family:'JetBrains Mono'; font-size:12px;">
        <div>單筆最大風險額: <b style="color:#EF4444;">${max_risk_dollars:.2f}</b></div>
        <div>單一持倉金額上限: <b style="color:#38BDF8;">${account_capital * (max_pos_cap/100):.2f}</b></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 2. 篩選股票池")
    watchlist_mode = st.selectbox(
        "選擇觀察池",
        ["J Law 核心動能觀察池 (精選 50 隻)", "S&P 500 & Nasdaq 100 高流動性 (100 隻)", "自訂 Ticker 清單"]
    )

    if watchlist_mode == "自訂 Ticker 清單":
        custom_input = st.text_area("輸入美股代碼 (以逗號隔開)", value="NVDA, TSLA, PLTR, AMD, COIN, MSTR, ARM, SMCI, TTD, BE")
        active_tickers = [x.strip().upper() for x in custom_input.split(",") if x.strip()]
    else:
        active_tickers = get_universe(watchlist_mode)

    st.markdown(f"**待掃描標的數:** `{len(active_tickers)}` 隻")
    scan_btn = st.button("⚡ 啟動 J Law 策略掃描", type="primary", use_container_width=True)

# ==========================================
# 8. 掃描與運算流程
# ==========================================
if scan_btn or 'jlaw_scan_results' not in st.session_state:
    with st.spinner("正在聯網下載高頻日線數據並進行 J Law 7 大維度量化計算..."):
        stock_dict, df_spy, df_qqq = fetch_market_and_stocks(active_tickers)
        
        if stock_dict is None or df_spy is None:
            st.error("❌ 無法取得 Yahoo Finance 數據，請檢查網絡連線或稍後再試。")
        else:
            market_info = analyze_market_regime(df_spy, df_qqq)
            results = []
            for ticker, df_t in stock_dict.items():
                res = calculate_stock_alpha(ticker, df_t, df_spy, df_qqq)
                if res is not None:
                    results.append(res)
            
            df_results = pd.DataFrame(results)
            if not df_results.empty:
                df_results = df_results.sort_values(by=['Score', 'RS'], ascending=[False, False]).reset_index(drop=True)
            
            st.session_state['jlaw_scan_results'] = df_results
            st.session_state['market_regime'] = market_info
            st.session_state['scan_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ==========================================
# 9. 主界面展示 (Dashboard Layout)
# ==========================================
st.title("🦅 J Law Alpha Hunter Pro 交易終端")
st.caption("量化遵循 J Law 波段交易原則：Stage 2 趨勢範式 · RS 領頭羊 · VCP 波動收窄 · DRSI 買點 · 1% 風險模型")

market_regime = st.session_state.get('market_regime', None)
if market_regime:
    st.markdown(f"""
    <div class="market-banner" style="background:{market_regime.get('bg', '#1E293B')}; border:1px solid {market_regime['color']};">
        <div>
            <span style="font-size:16px; font-weight:700; color:{market_regime['color']};">{market_regime['title']}</span>
            <div style="font-size:13px; color:#94A3B8; margin-top:4px;">{market_regime['desc']}</div>
        </div>
        <div style="text-align:right;">
            <span class="badge {'badge-green' if market_regime['allow_trades'] else 'badge-red'}">
                {'允許積極進場' if market_regime['allow_trades'] else '嚴格控制防守'}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

df_all = st.session_state.get('jlaw_scan_results', pd.DataFrame())

if df_all.empty:
    st.info("請點擊左側側邊欄「啟動 J Law 策略掃描」按鈕以獲取即時評估。")
    st.stop()

top_diamonds = len(df_all[df_all['Rank'] == 'Diamond'])
top_golds = len(df_all[df_all['Rank'] == 'Gold'])
avg_rs = int(df_all['RS'].mean()) if not df_all.empty else 0

m1, m2, m3, m4 = st.columns(4)
m1.metric("掃描總股票數", f"{len(df_all)} 隻")
m2.metric("💎 鑽石級獵殺名單 (Diamond)", f"{top_diamonds} 隻")
m3.metric("🥇 黃金級優質標的 (Gold)", f"{top_golds} 隻")
m4.metric("觀察池平均 RS 強度", f"{avg_rs} / 99")

st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 頂級獵殺名單 (Alpha Top Picks)",
    "📊 全市場多維度篩選器 (Screener)",
    "📈 個股深度診斷與圖表 (Deep Dive)",
    "🛡️ J Law 風控與倉位計算器 (Position Sizer)",
    "💼 模擬持倉與交易紀錄 (Portfolio)"
])

with tab1:
    st.markdown("### 🔥 最具交易價值 (Highest Opportunity Alpha)")
    
    top_candidates = df_all[df_all['Rank'].isin(['Diamond', 'Gold'])]
    if top_candidates.empty:
        top_candidates = df_all.head(6)
        st.warning("⚠️ 今日市場中無完全符合「鑽石級」完美形態標的，以下展示綜合評分最高的前 6 隻標的：")
    else:
        top_candidates = top_candidates.head(8)

    for idx, row in top_candidates.iterrows():
        risk_per_share = row['Entry'] - row['Stop']
        ideal_shares = int(max_risk_dollars / risk_per_share) if risk_per_share > 0 else 0
        total_cost = ideal_shares * row['Entry']
        max_cost = account_capital * (max_pos_cap / 100.0)
        if total_cost > max_cost:
            ideal_shares = int(max_cost / row['Entry'])
            total_cost = ideal_shares * row['Entry']

        card_class = "card-diamond" if row['Rank'] == "Diamond" else "card-gold"
        badge_class = "badge-diamond" if row['Rank'] == "Diamond" else "badge-gold"
        
        c1, c2 = st.columns()
        
        with c1:
            st.markdown(f"""
            <div class="{card_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="badge {badge_class}">{row['Rank']} TIER</span>
                    <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8;">SCORE {row['Score']}</span>
                </div>
                <div style="font-size:36px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0; color:#FFF;">
                    {row['Symbol']}
                </div>
                <div style="font-size:18px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row['Change'] >= 0 else '#EF4444'};">
                    ${row['Price']:.2f} ({'+' if row['Change']>0 else ''}{row['Change']:.2f}%)
                </div>
                <div style="margin-top:10px; font-size:12px; color:#94A3B8;">
                    RS 強度評分: <b style="color:#FFF;">{row['RS']}</b> / 99<br>
                    Stage 2 趨勢範式: <b style="color:#FFF;">{row['Stage2']}</b><br>
                    DRSI 狀態: <b style="color:#FFF;">{row['DRSI_Status']}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"#### 🎯 J Law 交易計劃與信號診斷 ({row['Symbol']})")
            
            tags_html = " ".join([f"<span class='badge badge-cyan'>{reason}</span>" for reason in row['Reasons']])
            st.markdown(tags_html, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="plan-box">
                <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap: 10px;">
                    <div>🔵 <b>建議買入 (Entry):</b><br><span style="font-size:16px; color:#38BDF8;">${row['Entry']:.2f}</span></div>
                    <div>🔴 <b>防守止損 (Stop):</b><br><span style="font-size:16px; color:#EF4444;">${row['Stop']:.2f} ({row['Stop_Pct']}%)</span></div>
                    <div>🟢 <b>目標 1 (2R):</b><br><span style="font-size:16px; color:#10B981;">${row['Target_2R']:.2f}</span></div>
                    <div>🌟 <b>目標 2 (3R):</b><br><span style="font-size:16px; color:#F59E0B;">${row['Target_3R']:.2f}</span></div>
                </div>
                <hr style="border:0; border-top:1px solid #1E293B; margin:10px 0;">
                <div style="display:flex; justify-content:space-between; font-size:13px; color:#94A3B8;">
                    <span>📐 <b>推薦股數:</b> <b style="color:#FFF;">{ideal_shares} 股</b></span>
                    <span>💵 <b>所需資金:</b> <b style="color:#FFF;">${total_cost:.2f}</b> ({total_cost/account_capital*100:.1f}% 倉位)</span>
                    <span>🛡️ <b>承受風險額:</b> <b style="color:#EF4444;">${risk_per_share * ideal_shares:.2f}</b> ({risk_pct}%)</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            btn_col1, btn_col2 = st.columns()
            with btn_col1:
                if st.button(f"⚡ 記錄買入 {row['Symbol']}", key=f"buy_{row['Symbol']}", use_container_width=True):
                    ok, msg = execute_trade(row['Symbol'], row['Entry'], row['Stop'], row['Target_2R'], row['Target_3R'], ideal_shares, risk_per_share * ideal_shares)
                    if ok: st.success(msg)
                    else: st.warning(msg)

        st.divider()

with tab2:
    st.markdown("### 📊 完整掃描結果篩選器")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        min_score = st.slider("最低綜合評分", 0, 100, 50, step=5)
    with col_f2:
        min_rs = st.slider("最低 RS Rating (1-99)", 1, 99, 70, step=5)
    with col_f3:
        only_stage2 = st.checkbox("僅看符合 Stage 2 股票", value=False)
    with col_f4:
        selected_ranks = st.multiselect("評級過濾", ["Diamond", "Gold", "Silver", "Bronze"], default=["Diamond", "Gold", "Silver"])

    df_filtered = df_all.copy()
    df_filtered = df_filtered[df_filtered['Score'] >= min_score]
    df_filtered = df_filtered[df_filtered['RS'] >= min_rs]
    df_filtered = df_filtered[df_filtered['Rank'].isin(selected_ranks)]
    if only_stage2:
        df_filtered = df_filtered[df_filtered['Stage2'] == "✅ 是"]

    st.caption(f"共篩選出 **{len(df_filtered)}** 隻符合條件的標的：")
    
    display_cols = [
        'Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Stage2',
        'DRSI_Status', 'RVOL', 'Dist_20EMA', 'Dist_52H', 'Entry', 'Stop', 'Stop_Pct', 'Target_2R'
    ]
    
    st.dataframe(
        df_filtered[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
            "RS": st.column_config.ProgressColumn("RS 相對強度", min_value=1, max_value=99, format="%d"),
            "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
            "Price": st.column_config.NumberColumn("現價 ($)", format="$%.2f"),
            "Entry": st.column_config.NumberColumn("買入價 ($)", format="$%.2f"),
            "Stop": st.column_config.NumberColumn("止損價 ($)", format="$%.2f"),
            "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
            "Target_2R": st.column_config.NumberColumn("2R 目標 ($)", format="$%.2f"),
            "Dist_20EMA": st.column_config.NumberColumn("距 20EMA (%)", format="%.1f%%"),
            "Dist_52H": st.column_config.NumberColumn("距 52H (%)", format="%.1f%%"),
            "RVOL": st.column_config.NumberColumn("相對量能", format="%.2fx")
        }
    )

with tab3:
    st.markdown("### 📈 個股深度診斷與 TradingView 互動 K 線圖")
    selected_ticker = st.selectbox("請選擇診斷標的", df_all['Symbol'].tolist(), index=0)
    
    target_row = df_all[df_all['Symbol'] == selected_ticker].iloc[0]
    
    col_d1, col_d2 = st.columns()
    
    with col_d1:
        st.markdown(f"#### 📋 {selected_ticker} J Law 7 維檢核雷達")
        
        check_items = [
            ("1. Stage 2 趨勢範式", target_row['Stage2'] == "✅ 是", "價格 > 50SMA > 150SMA > 200SMA，且均線向上"),
            ("2. RS 領頭羊地位 (≥80)", target_row['RS'] >= 80, f"當前 RS: {target_row['RS']} (超過 80% 大盤股票)"),
            ("3. VCP 波動收窄蓄勢", "VCP 波動收窄" in target_row['Reasons'], "近期波動度 (ATR) 明顯收斂"),
            ("4. DRSI 買點信號", "金叉" in target_row['DRSI_Status'], f"當前狀態: {target_row['DRSI_Status']}"),
            ("5. 20 EMA 關鍵支撐", abs(target_row['Dist_20EMA']) <= 3.0, f"距離 20 EMA: {target_row['Dist_20EMA']}%"),
            ("6. 突破量能 / 量能乾涸", target_row['RVOL'] >= 1.2 or target_row['RVOL'] < 0.75, f"相對成交量 (RVOL): {target_row['RVOL']}x"),
            ("7. 優良盈虧比 (≥ 2:1)", abs(target_row['Stop_Pct']) <= 7.0, f"止損空間僅 {abs(target_row['Stop_Pct'])}%，提供足夠 R:R 空間")
        ]
        
        for name, passed, desc in check_items:
            icon = "✅" if passed else "❌"
            color = "#10B981" if passed else "#EF4444"
            st.markdown(f"""
            <div style="background:#151D2E; border-left:3px solid {color}; padding:8px 12px; margin-bottom:8px; border-radius:4px;">
                <div style="font-weight:600; font-size:14px; color:#FFF;">{icon} {name}</div>
                <div style="font-size:12px; color:#94A3B8;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            
    with col_d2:
        st.markdown(f"#### 📊 {selected_ticker} TradingView 即時圖表")
        tv_widget = f"""
        <div class="tradingview-widget-container" style="height:480px;width:100%;">
          <div id="tradingview_{selected_ticker}" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
            "autosize": true,
            "symbol": "{selected_ticker}",
            "interval": "D",
            "timezone": "America/New_York",
            "theme": "dark",
            "style": "1",
            "locale": "zh_TW",
            "toolbar_bg": "#121824",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_{selected_ticker}"
          }}
          );
          </script>
        </div>
        """
        components.html(tv_widget, height=500)

with tab4:
    st.markdown("### 🛡️ J Law 專業風控與資金管理計算機")
    st.caption("核心理念：先看風險，再算獲利。單筆交易虧損金額必須被嚴格鎖定在總資產的 1%～2%。")
    
    c_calc1, c_calc2 = st.columns(2)
    with c_calc1:
        c_sym = st.selectbox("選擇計算股票", df_all['Symbol'].tolist(), index=0, key="calc_sym")
        c_row = df_all[df_all['Symbol'] == c_sym].iloc[0]
        
        calc_entry = st.number_input("計劃買入價 ($)", value=float(c_row['Entry']), step=0.5)
        calc_stop = st.number_input("計劃止損價 ($)", value=float(c_row['Stop']), step=0.5)
        calc_risk_pct = st.slider("本筆交易風險比例 (%)", 0.5, 3.0, float(risk_pct), 0.1)
        
    with c_calc2:
        risk_dollar_allowed = account_capital * (calc_risk_pct / 100.0)
        risk_per_share_calc = calc_entry - calc_stop
        
        if risk_per_share_calc <= 0:
            st.error("止損價必須低於買入價！")
        else:
            rec_shares = int(risk_dollar_allowed / risk_per_share_calc)
            rec_pos_val = rec_shares * calc_entry
            pos_ratio = (rec_pos_val / account_capital) * 100
            
            t1_val = calc_entry + (2.0 * risk_per_share_calc)
            t2_val = calc_entry + (3.0 * risk_per_share_calc)
            
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #38BDF8;">
                <h4 style="margin:0 0 10px 0; color:#38BDF8;">📐 最佳下單分配模型 ({c_sym})</h4>
                <div style="font-family:'JetBrains Mono'; font-size:15px; line-height:1.8;">
                    <div>• 總賬戶資產: <b>${account_capital:,.2f}</b></div>
                    <div>• 允許最大虧損 (1R): <b style="color:#EF4444;">${risk_dollar_allowed:,.2f}</b> ({calc_risk_pct}%)</div>
                    <div>• 每股承受風險: <b style="color:#EF4444;">${risk_per_share_calc:.2f}</b> ({(risk_per_share_calc/calc_entry)*100:.2f}%)</div>
                    <hr style="border:0; border-top:1px solid #1E293B; margin:8px 0;">
                    <div>• <b>建議購買股數:</b> <span style="font-size:20px; color:#10B981; font-weight:700;">{rec_shares} 股</span></div>
                    <div>• <b>總持倉金額:</b> <b>${rec_pos_val:,.2f}</b> ({pos_ratio:.1f}% 倉位)</div>
                    <hr style="border:0; border-top:1px solid #1E293B; margin:8px 0;">
                    <div>• <b>第 1 止盈目標 (2R):</b> <b style="color:#10B981;">${t1_val:.2f}</b> (平半倉 + 止損移至保本)</div>
                    <div>• <b>第 2 止盈目標 (3R):</b> <b style="color:#F59E0B;">${t2_val:.2f}</b> (鎖定超額利潤)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if pos_ratio > max_pos_cap:
                st.warning(f"⚠️ 警告：該倉位金額佔總資金 {pos_ratio:.1f}%，超過你設定的單一持倉上限 ({max_pos_cap}%)！建議下調股數至 {int((account_capital*(max_pos_cap/100))/calc_entry)} 股。")

with tab5:
    st.markdown("### 💼 我的持倉與風險監控")
    if os.path.exists(PORTFOLIO_FILE):
        port_df = pd.read_csv(PORTFOLIO_FILE)
        if not port_df.empty:
            st.dataframe(port_df, use_container_width=True, hide_index=True)
            if st.button("🗑️ 清空所有模擬持倉紀錄"):
                os.remove(PORTFOLIO_FILE)
                init_db()
                st.rerun()
        else:
            st.info("目前無任何持倉。可在「🏆 頂級獵殺名單」中點擊「記錄買入」按鈕建立倉位。")
    else:
        st.info("目前無持倉紀錄。")
