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
st.set_page_config(
    page_title="J Law Alpha Hunter • Tesla Cyber Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. Tesla 旗艦級科技美學主題 (Tesla Cyber UI)
# ==========================================
def inject_tesla_theme():
    tesla_bg_url = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=2000&q=80"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Tesla 全局背景 */
        .stApp {{
            background: linear-gradient(180deg, rgba(8, 11, 16, 0.90) 0%, rgba(11, 14, 20, 0.97) 100%),
                        url('{tesla_bg_url}') no-repeat center center fixed;
            background-size: cover;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
        }}
        
        /* 側邊欄磨砂黑風格 */
        section[data-testid="stSidebar"] {{
            background: rgba(10, 14, 23, 0.95) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}
        
        /* Tesla 實體車機質感按鈕 */
        div.stButton > button:first-child {{
            background: linear-gradient(135deg, #1e2430 0%, #0d1017 100%);
            color: #FFFFFF;
            border: 1px solid #E82127; /* Tesla 經典火紅 */
            border-radius: 4px;
            padding: 10px 24px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            box-shadow: 0 4px 15px rgba(232, 33, 39, 0.25);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
        }}
        div.stButton > button:first-child:hover {{
            background: #E82127;
            color: #FFFFFF;
            border-color: #FF4D4D;
            box-shadow: 0 0 25px rgba(232, 33, 39, 0.7), 0 0 10px rgba(232, 33, 39, 0.9);
            transform: translateY(-2px);
        }}

        /* Tesla 玻璃磨砂卡片 */
        .cyber-card {{
            background: rgba(18, 24, 38, 0.78);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            transition: all 0.25s ease;
        }}
        .cyber-card:hover {{
            border-color: #E82127;
            box-shadow: 0 8px 30px rgba(232, 33, 39, 0.2);
        }}
        
        .card-diamond {{
            border-left: 4px solid #06B6D4 !important;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        }}
        .card-gold {{
            border-left: 4px solid #EAB308 !important;
            background: linear-gradient(135deg, rgba(234, 179, 8, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        }}
        
        /* 標籤徽章 */
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
            margin-right: 6px;
            margin-bottom: 4px;
        }}
        .badge-diamond {{ background: rgba(6, 182, 212, 0.25); color: #22D3EE; border: 1px solid #06B6D4; }}
        .badge-gold {{ background: rgba(234, 179, 8, 0.25); color: #FACC15; border: 1px solid #EAB308; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-cyan {{ background: rgba(14, 165, 233, 0.2); color: #38BDF8; border: 1px solid #0284C7; }}
        .badge-tesla {{ background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }}

        /* 模組標題光條 */
        .section-header {{
            background: rgba(15, 23, 42, 0.88);
            border-left: 5px solid #E82127;
            padding: 14px 20px;
            border-radius: 6px;
            margin: 20px 0 16px 0;
            backdrop-filter: blur(10px);
        }}
        
        .action-box {{
            background: rgba(10, 15, 26, 0.92);
            border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px;
            padding: 20px;
            font-family: 'JetBrains Mono', monospace;
        }}
        
        /* Tesla 頂部標誌性 Banner */
        .tesla-banner {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(18, 24, 38, 0.8);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 16px 22px;
            margin-bottom: 22px;
            backdrop-filter: blur(12px);
        }}

        /* 情境推演卡片 */
        .scenario-box {{
            background: rgba(15, 23, 42, 0.7);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 6px;
            padding: 14px;
            font-size: 13px;
            line-height: 1.6;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 標的池定義 (核心自選標的對齊每日任務)
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

# ==========================================
# 3. 數據獲取引擎 (三大官方基準指數 + 全股)
# ==========================================
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_all_data(tickers):
    needed_symbols = list(set(tickers + ['SPY', 'QQQ', 'DIA']))
    try:
        data = yf.download(needed_symbols, period="1y", interval="1d", progress=False, group_by='ticker', threads=True)
    except Exception:
        return None, None, None, None

    if data is None or data.empty:
        return None, None, None, None

    def extract_clean_df(raw_data, sym):
        try:
            if isinstance(raw_data.columns, pd.MultiIndex):
                if sym in raw_data.columns.levels[0]:
                    df = raw_data[sym].copy()
                elif sym in raw_data.columns.levels:
                    df = raw_data.xs(sym, axis=1, level=1).copy()
                else:
                    return None
            else:
                df = raw_data.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception:
            return None

    df_spy = extract_clean_df(data, 'SPY')
    df_qqq = extract_clean_df(data, 'QQQ')
    df_dia = extract_clean_df(data, 'DIA')
    
    stocks = {}
    for s in tickers:
        df_s = extract_clean_df(data, s)
        if df_s is not None and len(df_s) >= 140:
            stocks[s] = df_s

    return stocks, df_spy, df_qqq, df_dia

# ==========================================
# 4. J Law 結構性定價與 7 維度核心演算法
# ==========================================
def evaluate_jlaw_stock(symbol, df, df_spy):
    try:
        c = df['Close']
        h = df['High']
        l = df['Low']
        v = df['Volume']
        
        curr_price = float(c.iloc[-1])
        prev_price = float(c.iloc[-2])
        change_pct = ((curr_price - prev_price) / prev_price) * 100

        # 均線系統
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma150 = float(c.rolling(150).mean().iloc[-1]) if len(c) >= 150 else sma50
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma150
        sma200_20d_ago = float(c.rolling(200).mean().iloc[-20]) if len(c) >= 220 else sma200

        # 52 週高低位
        roll_len = min(len(c), 252)
        h52 = float(h.iloc[-roll_len:].max())
        l52 = float(l.iloc[-roll_len:].min())
        dist_h52 = ((curr_price - h52) / h52) * 100
        dist_l52 = ((curr_price - l52) / l52) * 100

        reasons = []
        score = 0

        # 1. Stage 2 趨勢檢核
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 15
            if sma200 >= sma200_20d_ago:
                score += 5
            if dist_h52 >= -25.0 and dist_l52 >= 25.0:
                score += 5
                is_stage2 = True
                reasons.append("Stage 2 完美多頭範式")
        elif curr_price > sma50:
            score += 8
            if dist_h52 >= -20.0:
                reasons.append("50SMA 上方強勢整理")

        # 2. 加權百分位 RS 相對強度 Rating
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w_perf = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w_perf = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_diff = (stock_w_perf - spy_w_perf) * 100
        rs_rating = int(np.clip(50 + (rs_diff * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            reasons.append(f"強勢領頭羊 (RS Rating {rs_rating})")
        elif rs_rating >= 65:
            score += 18
            reasons.append(f"優於大盤 (RS {rs_rating})")
        elif rs_rating >= 50:
            score += 10

        # 3. VCP 波動收窄與緊密收市
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 10
            reasons.append("VCP 波動度收斂蓄勢")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市 (Tight Closes)")

        # 4. DRSI (Stoch RSI) 買點
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_k = 100 * (rsi - rsi.rolling(14).min()) / ((rsi.rolling(14).max() - rsi.rolling(14).min()).replace(0, 1e-9))
        stoch_d = stoch_k.rolling(3).mean()
        k_val = float(stoch_k.iloc[-1])
        d_val = float(stoch_d.iloc[-1])
        prev_k = float(stoch_k.iloc[-2])
        prev_d = float(stoch_d.iloc[-2])

        drsi_status = "中性"
        if prev_k <= prev_d and k_val > d_val:
            if k_val < 35:
                score += 15
                drsi_status = "超賣金叉 (絕佳買點)"
                reasons.append("DRSI 超賣區向上金叉")
            else:
                score += 12
                drsi_status = "多頭金叉 (順勢買點)"
                reasons.append("DRSI 多頭動能金叉轉強")
        elif k_val > d_val:
            score += 8
            drsi_status = "多頭維持"
        elif k_val < 25:
            score += 6
            drsi_status = "超賣醞釀"

        # 5. 20 EMA 關鍵支撐
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
        if 0 <= dist_ema20 <= 2.5:
            score += 10
            reasons.append("回踩 20 EMA 支撐買區")
        elif -2.0 <= dist_ema20 < 0:
            score += 6
            reasons.append("回測 20 EMA 關鍵均線")
        elif 2.5 < dist_ema20 <= 6.0:
            score += 5

        # 6. 量能分析
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"放量突破 (RVOL {rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量能乾涸 (VDU 洗盤完成)")
        else:
            score += 4

        total_score = int(np.clip(score, 0, 100))
        
        if total_score >= 80 and is_stage2:
            rank = "Diamond"
        elif total_score >= 65:
            rank = "Gold"
        elif total_score >= 50:
            rank = "Silver"
        else:
            rank = "Bronze"

        # ============================================================
        # 7. J Law 結構性定價計算 (非盲目現價買！)
        # ============================================================
        recent_10d_high = float(h.iloc[-10:].max())
        recent_10d_low = float(l.iloc[-10:].min())
        
        if dist_ema20 <= 3.0:
            setup_type = "20 EMA 回踩低吸點"
            calc_entry = round(ema20 * 1.003, 2)
            calc_stop = round(min(ema20 * 0.965, calc_entry - (1.5 * atr14)), 2)
        else:
            setup_type = "VCP 阻力樞紐突破點"
            calc_entry = round(recent_10d_high * 1.002, 2)
            calc_stop = round(max(recent_10d_low * 0.99, calc_entry - (1.5 * atr14)), 2)

        # 止損風控限制在 3% 到 7.5% 之間
        calc_stop = min(calc_stop, round(calc_entry * 0.97, 2))
        calc_stop = max(calc_stop, round(calc_entry * 0.925, 2))
        
        risk_per_share = round(calc_entry - calc_stop, 2)
        stop_pct = round(((calc_stop - calc_entry) / calc_entry) * 100, 2)

        target_2r = round(calc_entry + (2.0 * risk_per_share), 2)
        target_3r = round(calc_entry + (3.0 * risk_per_share), 2)
        entry_diff = round(((curr_price - calc_entry) / calc_entry) * 100, 2)

        # 技術指標深度對齊
        rsi_val = round(float(rsi.iloc[-1]), 1)
        ema12 = c.ewm(span=12, adjust=False).mean()
        ema26 = c.ewm(span=26, adjust=False).mean()
        macd_dif = float((ema12 - ema26).iloc[-1])
        macd_dea = float((ema12 - ema26).ewm(span=9, adjust=False).mean().iloc[-1])
        macd_bias = "多頭向上" if macd_dif > macd_dea else "死叉回調"

        return {
            "Symbol": symbol,
            "Rank": rank,
            "Score": total_score,
            "Price": round(curr_price, 2),
            "Change": round(change_pct, 2),
            "RS": rs_rating,
            "Stage2": "是 (符合)" if is_stage2 else "否",
            "DRSI_Status": drsi_status,
            "RVOL": round(rvol, 2),
            "Dist_20EMA": round(dist_ema20, 2),
            "Setup_Type": setup_type,
            "Entry": calc_entry,
            "Entry_Diff": entry_diff,
            "Stop": calc_stop,
            "Stop_Pct": stop_pct,
            "Target_2R": target_2r,
            "Target_3R": target_3r,
            "Risk_Per_Share": risk_per_share,
            "RSI": rsi_val,
            "MACD_Status": macd_bias,
            "EMA20": round(ema20, 2),
            "SMA50": round(sma50, 2),
            "SMA200": round(sma200, 2),
            "Pivot_High": round(recent_10d_high, 2),
            "Pivot_Low": round(recent_10d_low, 2),
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用邏輯與介面渲染
# ==========================================
inject_tesla_theme()

# 左側極簡 Cyber 側邊欄
with st.sidebar:
    st.markdown("## ⚡ TESLA CYBER")
    st.caption("Autonomous Swing Trading Desk")
    st.markdown("---")

    st.markdown("""
    <div style="background:rgba(232, 33, 39, 0.12); border:1px solid #E
