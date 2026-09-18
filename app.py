import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import requests
import datetime

# ==========================================
# 0. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="TESLA CYBER TERMINAL • J LAW ALPHA & FLOW",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 1. TESLA CYBERCAB & OPTIMUS 旗艦級科技美學 CSS
# ==========================================
def inject_tesla_cyber_theme():
    # 融合 Cybercab 與 Optimus 科技氛圍底圖
    cyber_bg = "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=2600&q=80"
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap');
        
        .block-container {{
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 98% !important;
        }}

        /* Tesla OLED 深邃黑階 + Cybercab 金屬光澤壁紙 */
        .stApp {{
            background: linear-gradient(180deg, rgba(5, 7, 13, 0.94) 0%, rgba(9, 13, 22, 0.98) 100%),
                        url('{cyber_bg}') no-repeat center center fixed;
            background-size: cover;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* 側邊欄拉絲不鏽鋼與毛玻璃 */
        section[data-testid="stSidebar"] {{
            background: rgba(8, 12, 19, 0.96) !important;
            backdrop-filter: blur(28px);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }}

        /* Tesla 車機頂部狀態欄 */
        .tesla-os-header {{
            background: rgba(13, 18, 29, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-top: 3px solid #E82127;
            border-radius: 8px;
            padding: 14px 22px;
            margin-bottom: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(20px);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.6);
        }}

        /* PRND 檔位控制器 */
        .tesla-gear-box {{
            display: inline-flex;
            background: rgba(5, 8, 14, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 6px;
            padding: 3px 6px;
            gap: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 900;
            font-size: 13px;
        }}
        .gear-item {{
            padding: 4px 10px;
            border-radius: 4px;
            color: #475569;
        }}
        .gear-active-drive {{
            background: #10B981;
            color: #000 !important;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.7);
        }}
        .gear-active-neutral {{
            background: #F59E0B;
            color: #000 !important;
            box-shadow: 0 0 14px rgba(245, 158, 11, 0.7);
        }}
        .gear-active-park {{
            background: #E82127;
            color: #FFF !important;
            box-shadow: 0 0 14px rgba(232, 33, 39, 0.8);
        }}

        /* 導航 Radio：全自適應 Cyber 膠囊按鈕 */
        div[role="radiogroup"] {{
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            background: rgba(12, 16, 26, 0.75) !important;
            padding: 6px !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            margin-bottom: 16px !important;
        }}
        div[role="radiogroup"] > label {{
            background: rgba(19, 25, 39, 0.7) !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 6px !important;
            padding: 8px 18px !important;
            color: #94A3B8 !important;
            cursor: pointer !important;
            transition: all 0.25s ease !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }}
        div[role="radiogroup"] > label:hover {{
            border-color: #E82127 !important;
            color: #FFF !important;
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.35) !important;
        }}
        div[role="radiogroup"] input[type="radio"] {{
            display: none !important;
        }}
        div[role="radiogroup"] > label:has(input:checked) {{
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.35) 0%, rgba(19, 25, 39, 0.95) 100%) !important;
            border-color: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 18px rgba(232, 33, 39, 0.5) !important;
        }}

        /* Cybertruck & Cybercab 切角資訊卡片 */
        .cyber-card {{
            background: rgba(14, 19, 31, 0.85);
            backdrop-filter: blur(18px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.5);
            transition: all 0.25s ease;
            min-height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .cyber-card:hover {{
            border-color: #E82127;
            box-shadow: 0 12px 32px rgba(232, 33, 39, 0.3);
            transform: translateY(-2px);
        }}
        
        /* 標籤徽章：絕對鎖定單行 */
        .badge {{
            display: inline-flex;
            align-items: center;
            white-space: nowrap !important;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10.5px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
        }}
        .badge-diamond {{ background: rgba(6, 182, 212, 0.2); color: #22D3EE; border: 1px solid #06B6D4; }}
        .badge-gold {{ background: rgba(234, 179, 8, 0.2); color: #FACC15; border: 1px solid #EAB308; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-tesla {{ background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }}
        .badge-flow {{ background: rgba(168, 85, 247, 0.25); color: #C084FC; border: 1px solid #A855F7; }}

        /* Tesla HUD 數據盒 */
        .hud-telemetry {{
            background: rgba(12, 16, 26, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid #E82127;
            border-radius: 6px;
            padding: 12px 16px;
        }}
        .hud-title {{
            font-size: 10.5px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 1px;
        }}
        .hud-val {{
            font-size: 24px;
            font-weight: 900;
            color: #FFF;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
        }}

        .section-header {{
            background: rgba(14, 19, 31, 0.9);
            border-left: 4px solid #E82127;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 14px;
        }}

        .action-box {{
            background: rgba(9, 13, 22, 0.95);
            border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px;
            padding: 18px;
            font-family: 'JetBrains Mono', monospace;
        }}

        @keyframes pulse-tesla {{
            0% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(232, 33, 39, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0); }}
        }}
        .alert-tesla {{
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.25) 0%, rgba(14, 19, 31, 0.95) 100%);
            border: 1px solid #E82127;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 14px;
            animation: pulse-tesla 2s infinite;
        }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 標的清單與統一表格配置
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

GRID_COLUMN_CONFIG = {
    "Symbol": st.column_config.TextColumn("標的代碼"),
    "Rank": st.column_config.TextColumn("評級"),
    "Price": st.column_config.NumberColumn("最新收市 ($)", format="$%.2f"),
    "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
    "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
    "RS": st.column_config.ProgressColumn("RS 相對強度", min_value=1, max_value=99, format="%d"),
    "Flow_Status": st.column_config.TextColumn("主力資金異動"),
    "CMF": st.column_config.NumberColumn("20D CMF", format="%.2f"),
    "Pocket_Pivot": st.column_config.TextColumn("暗盤口袋買點"),
    "Setup_Type": st.column_config.TextColumn("戰術型態"),
    "Entry": st.column_config.NumberColumn("樞紐買點 ($)", format="$%.2f"),
    "Entry_Diff": st.column_config.NumberColumn("距買點 (%)", format="%.2f%%"),
    "Stop": st.column_config.NumberColumn("結構止損 ($)", format="$%.2f"),
    "Stop_Pct": st.column_config.NumberColumn("止損幅度 (%)", format="%.2f%%"),
    "Target_2R": st.column_config.NumberColumn("趁強平半 (2R)", format="$%.2f"),
    "Target_3R": st.column_config.NumberColumn("趁弱移停 (3R)", format="$%.2f"),
    "RVOL": st.column_config.NumberColumn("量比 RVOL", format="%.2fx")
}

# ==========================================
# 3. 數據獲取引擎
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
                if sym in raw_data.columns.levels[0]: df = raw_data[sym].copy()
                elif sym in raw_data.columns.levels: df = raw_data.xs(sym, axis=1, level=1).copy()
                else: return None
            else:
                df = raw_data.copy()
            df = df.dropna(subset=['Close'])
            return df if len(df) >= 120 else None
        except Exception:
            return None

    df_spy = extract_clean_df(data, 'SPY')
    df_qqq = extract_clean_df(data, 'QQQ')
    df_dia = extract_clean_df(data, 'DIA')
    stocks = {s: extract_clean_df(data, s) for s in tickers if extract_clean_df(data, s) is not None}
    return stocks, df_spy, df_qqq, df_dia

# ==========================================
# 4. 資金面量化與 J Law M.E.T.A. 核心演算法
# ==========================================
def calculate_distribution_days(df, lookback=25):
    """計算基準指數過去 lookback 天的主力出貨日 (Distribution Days)"""
    if df is None or len(df) < lookback + 1:
        return 0
    recent = df.iloc[-lookback:].copy()
    prev_close = df['Close'].shift(1).iloc[-lookback:]
    prev_vol = df['Volume'].shift(1).iloc[-lookback:]
    
    # 出貨日定義：下跌超過 0.2% 且成交量大於前一日
    is_dist = (recent['Close'] < prev_close * 0.998) & (recent['Volume'] > prev_vol)
    return int(is_dist.sum())

def evaluate_jlaw_stock(symbol, df, df_spy):
    try:
        c, h, l, v = df['Close'], df['High'], df['Low'], df['Volume']
        curr_price = float(c.iloc[-1])
        prev_price = float(c.iloc[-2])
        change_pct = ((curr_price - prev_price) / prev_price) * 100

        ema10 = float(c.ewm(span=10, adjust=False).mean().iloc[-1])
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma150 = float(c.rolling(150).mean().iloc[-1]) if len(c) >= 150 else sma50
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma150
        sma200_20d_ago = float(c.rolling(200).mean().iloc[-20]) if len(c) >= 220 else sma200

        roll_len = min(len(c), 252)
        h52 = float(h.iloc[-roll_len:].max())
        l52 = float(l.iloc[-roll_len:].min())
        dist_h52 = ((curr_price - h52) / h52) * 100
        dist_l52 = ((curr_price - l52) / l52) * 100

        reasons = []
        score = 0
        meta_edges = 0

        # ----------------------------------------------------
        # 資金面深度指標 (Smart Money Flow Analysis)
        # ----------------------------------------------------
        # 1. 20日 CMF 蔡金資金流量 (Chaikin Money Flow)
        hl_diff = (h - l).replace(0, 1e-9)
        mf_multiplier = ((c - l) - (h - c)) / hl_diff
        mf_volume = mf_multiplier * v
        cmf_20 = float(mf_volume.rolling(20).sum().iloc[-1] / v.rolling(20).sum().replace(0, 1e-9).iloc[-1])
        
        # 2. Pocket Pivot (機構口袋買點 / 暗盤偷步異動)
        # 定義：今日上漲，且成交量大於過去 10 個交易日內「最大陰燭」的成交量
        is_up_today = curr_price > prev_price
        last_10_down_vol = [v.iloc[-(i+1)] for i in range(1, 11) if c.iloc[-(i+1)] < c.iloc[-(i+2)]]
        max_down_vol = max(last_10_down_vol) if last_10_down_vol else 0
        is_pocket_pivot = is_up_today and (v.iloc[-1] > max_down_vol) and (curr_price >= ema10 * 0.98)

        # 3. 50日多空成交量攻防比 (Up/Down Volume Ratio)
        last_50_c = c.iloc[-50:]
        last_50_v = v.iloc[-50:]
        up_vol_sum = last_50_v[last_50_c > last_50_c.shift(1)].sum()
        down_vol_sum = last_50_v[last_50_c < last_50_c.shift(1)].sum()
        up_down_ratio = float(up_vol_sum / (down_vol_sum if down_vol_sum > 0 else 1e-9))

        # 主力資金評級定性
        if cmf_20 > 0.15 or (is_pocket_pivot and cmf_20 > 0.05):
            flow_status = "🔥 主力強勢吸籌 (Accumulation)"
            score += 15
            reasons.append("主力大單持續淨流入")
        elif cmf_20 < -0.10:
            flow_status = "⚠️ 機構資金派發 (Distribution)"
            score -= 10
        else:
            flow_status = "⚖️ 資金中性沉澱 (Neutral)"

        if is_pocket_pivot:
            score += 10
            meta_edges += 1
            reasons.append("觸發 Pocket Pivot 口袋買點")

        # ----------------------------------------------------
        # J Law 冠軍技術維度 (Trend & Structure)
        # ----------------------------------------------------
        # 1. Stage 2 均線體系
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 20
            if sma200 >= sma200_20d_ago and dist_h52 >= -25.0 and dist_l52 >= 25.0:
                is_stage2 = True
                meta_edges += 1
                reasons.append("Stage 2 完美多頭架構")
        elif curr_price > sma50:
            score += 8

        # 2. 加權百分位 RS 強度
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_rating = int(np.clip(50 + ((stock_w - spy_w) * 100 * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            meta_edges += 1
            reasons.append(f"強勢領頭羊 (RS {rs_rating})")
        elif rs_rating >= 65:
            score += 15
            reasons.append(f"優於大盤 (RS {rs_rating})")
        elif rs_rating >= 50: score += 8

        # 3. VCP 波動收窄與緊密收市
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        is_vcp = False
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 12
            is_vcp = True
            meta_edges += 1
            reasons.append("VCP 波動收窄蓄勢")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市 (Tight Closes)")

        # 4. MA 均線支撐區 (Zone)
        dist_ema10 = ((curr_price - ema10) / ema10) * 100
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
        is_ma_support = False
        if 0 <= dist_ema20 <= 2.5 or 0 <= dist_ema10 <= 2.0:
            score += 15
            is_ma_support = True
            meta_edges += 1
            reasons.append("回踩 10/20 EMA 支撐區間")
        elif -2.0 <= dist_ema20 < 0:
            score += 8
            reasons.append("下探 20 EMA 關鍵均線")

        # 5. DRSI 動能金叉
        delta = c.diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / (loss.replace(0, 1e-9)))))
        stoch_k = 100 * (rsi - rsi.rolling(14).min()) / ((rsi.rolling(14).max() - rsi.rolling(14).min()).replace(0, 1e-9))
        stoch_d = stoch_k.rolling(3).mean()
        k_val, d_val = float(stoch_k.iloc[-1]), float(stoch_d.iloc[-1])
        prev_k, prev_d = float(stoch_k.iloc[-2]), float(stoch_d.iloc[-2])

        drsi_status = "中性"
        is_drsi_bullish = False
        if prev_k <= prev_d and k_val > d_val:
            is_drsi_bullish = True
            meta_edges += 1
            if k_val < 35:
                score += 15
                drsi_status = "超賣金叉 (絕佳買點)"
                reasons.append("DRSI 超賣金叉")
            else:
                score += 10
                drsi_status = "多頭金叉 (順勢起爆)"
                reasons.append("DRSI 多頭金叉")
        elif k_val > d_val:
            score += 6
            drsi_status = "多頭維持"

        # 6. 量能異動
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"爆量突破 (RVOL {rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量能乾涸 (VDU 沉澱)")

        total_score = int(np.clip(score, 0, 100))
        rank = "Diamond" if (total_score >= 80 and is_stage2) else ("Gold" if total_score >= 65 else ("Silver" if total_score >= 50 else "Bronze"))

        # 結構定價計算
        recent_10d_high = float(h.iloc[-10:].max())
        recent_10d_low = float(l.iloc[-10:].min())

        if is_ma_support or abs(dist_ema20) <= 2.5:
            setup_type = "M.E.T.A. Pullback 回踩買點"
            calc_entry = round(max(ema20, curr_price) * 1.002, 2)
            calc_stop = round(min(ema20 * 0.965, calc_entry - (1.5 * atr14)), 2)
        else:
            setup_type = "VCP Pivot 樞紐突破點"
            calc_entry = round(recent_10d_high * 1.002, 2)
            calc_stop = round(max(recent_10d_low * 0.99, calc_entry - (1.5 * atr14)), 2)

        calc_stop = min(calc_stop, round(calc_entry * 0.97, 2))
        calc_stop = max(calc_stop, round(calc_entry * 0.925, 2))
        
        risk_per_share = round(calc_entry - calc_stop, 2)
        stop_pct = round(((calc_stop - calc_entry) / calc_entry) * 100, 2)
        target_2r = round(calc_entry + (2.0 * risk_per_share), 2)
        target_3r = round(calc_entry + (3.0 * risk_per_share), 2)
        entry_diff = round(((curr_price - calc_entry) / calc_entry) * 100, 2)

        is_all_rules_met = (is_stage2 and rs_rating >= 80 and (is_drsi_bullish or is_vcp or is_pocket_pivot) and abs(entry_diff) <= 3.0)

        return {
            "Symbol": symbol,
            "Rank": rank,
            "Score": total_score,
            "Edges": meta_edges,
            "Price": round(curr_price, 2),
            "Change": round(change_pct, 2),
            "RS": rs_rating,
            "Flow_Status": flow_status,
            "CMF": round(cmf_20, 2),
            "Pocket_Pivot": "🔥 觸發" if is_pocket_pivot else "—",
            "UpDown_Ratio": round(up_down_ratio, 2),
            "Stage2": "符合" if is_stage2 else "否",
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
            "RSI": round(float(rsi.iloc[-1]), 1),
            "All_Rules_Met": is_all_rules_met,
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用渲染
# ==========================================
inject_tesla_cyber_theme()

with st.sidebar:
    st.markdown("## ⚡ TESLA CYBER")
    st.caption("Optimus Autonomous Terminal • J Law System")
    st.markdown("---")

    st.markdown("""
    <div style="background:rgba(232, 33, 39, 0.12); border:1px solid #E82127; border-radius:6px; padding:12px; margin-bottom:14px;">
        <div style="font-weight:900; color:#FF6B6B; font-size:12.5px;">🤖 OPTIMUS QUANT CORE</div>
        <div style="font-size:11px; color:#CBD5E1; margin-top:4px; line-height:1.5;">
            已啟動主力資金面追蹤引擎：大盤出貨日計數、CMF 蔡金資金流、Pocket Pivot 機構暗盤異動及 1% 倉位模型。
        </div>
    </div>
    """, unsafe_allow_html=True)

    custom_add = st.text_area("增補自選標的 (逗號分隔)", value="")
    custom_tickers = [x.strip().upper() for x in custom_add.split(",") if x.strip()]
    full_scan_list = list(dict.fromkeys(DEFAULT_UNIVERSE + custom_tickers))
    st.caption(f"全天候監控標的：**{len(full_scan_list)}** 隻")
    
    if st.button("⚡ 重新掃描市場 (RE-SCAN)"):
        st.session_state.pop('scan_data', None)
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔔 Telegram 警報推播")
    tg_token = st.text_input("Bot Token", type="password", placeholder="選填 Telegram Token")
    tg_chat_id = st.text_input("Chat ID", placeholder="選填 Chat ID")
    if tg_token and tg_chat_id:
        if st.button("📤 發送測試警報"):
            try:
                r = requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", 
                                  json={"chat_id": tg_chat_id, "text": "⚡ [Tesla Cyber Terminal] 主力資金異動與 J Law 系統已連線！", "parse_mode": "Markdown"}, timeout=5)
                if r.status_code == 200: st.success("發送成功！")
                else: st.error("發送失敗，請核對參數")
            except Exception as e:
                st.error(f"連線異常: {e}")

# 獲取行情
if 'scan_data' not in st.session_state:
    with st.spinner("⚡ Optimus 正在計算 52 隻美股主力資金流向與 J Law 樞紐..."):
        stock_dict, df_spy, df_qqq, df_dia = fetch_all_data(full_scan_list)
        if stock_dict is not None and df_spy is not None:
            results = [evaluate_jlaw_stock(sym, df_t, df_spy) for sym, df_t in stock_dict.items()]
            results = [r for r in results if r is not None]
            df_res = pd.DataFrame(results)
            if not df_res.empty:
                df_res = df_res.sort_values(by=['Score', 'RS'], ascending=[False, False]).reset_index(drop=True)
            st.session_state['scan_data'] = df_res
            st.session_state['market_indexes'] = {'SPY': df_spy, 'QQQ': df_qqq, 'DIA': df_dia}
        else:
            st.session_state['scan_data'] = pd.DataFrame()
            st.session_state['market_indexes'] = {}

df_results = st.session_state.get('scan_data', pd.DataFrame())
indexes = st.session_state.get('market_indexes', {})

# 計算大盤出貨日與狀態
qqq_df = indexes.get('QQQ')
spy_df = indexes.get('SPY')
qqq_dist_days = calculate_distribution_days(qqq_df, lookback=25)
spy_dist_days = calculate_distribution_days(spy_df, lookback=25)

qqq_curr = float(qqq_df['Close'].iloc[-1]) if qqq_df is not None else 0
qqq_ema20 = float(qqq_df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]) if qqq_df is not None else 0
spy_curr = float(spy_df['Close'].iloc[-1]) if spy_df is not None else 0
spy_sma50 = float(spy_df['Close'].rolling(50).mean().iloc[-1]) if spy_df is not None else 0

# 大盤檔位評定：結合均線與出貨日
if (qqq_curr > qqq_ema20 and spy_curr > spy_sma50) and (qqq_dist_days < 5 and spy_dist_days < 5):
    gear_class_d = "gear-active-drive"
    gear_class_n, gear_class_p = "", ""
    gear_text = "DRIVE (積極做多 / 滿油門)"
    recommended_exposure = 100
elif (qqq_curr > qqq_ema20 or spy_curr > spy_sma50) and (qqq_dist_days < 6):
    gear_class_n = "gear-active-neutral"
    gear_class_d, gear_class_p = "", ""
    gear_text = "NEUTRAL (中性輕倉 / 嚴控回撤)"
    recommended_exposure = 40
else:
    gear_class_p = "gear-active-park"
    gear_class_d, gear_class_n = "", ""
    gear_text = "PARK (空倉防守 / 主力派發)"
    recommended_exposure = 10

# 頂部 Tesla Cybercab & Optimus 狀態條
st.markdown(f"""
<div class="tesla-os-header">
    <div>
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:22px; font-weight:900; font-family:'JetBrains Mono'; color:#FFF; letter-spacing:1px;">
                ⚡ TESLA CYBER TERMINAL <span style="color:#E82127;">// SMART MONEY RADAR</span>
            </span>
            <span class="badge badge-tesla">CYBERCAB CONNECTED</span>
            <span class="badge badge-diamond">OPTIMUS GEN-3</span>
        </div>
        <div style="font-size:11.5px; color:#94A3B8; margin-top:3px;">
            INSTITUTIONAL LIQUIDITY TRACKER • J LAW CHAMPION TRADING DESK
        </div>
    </div>
    <div style="display:flex; align-items:center; gap:16px;">
        <div style="text-align:right;">
            <div style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono';">大盤檔位 TELEMETRY</div>
            <div style="font-size:12px; font-weight:700; color:#E2E8F0; margin-top:2px;">{gear_text}</div>
        </div>
        <div class="tesla-gear-box">
            <span class="gear-item {gear_class_p}">P</span>
            <span class="gear-item">R</span>
            <span class="gear-item {gear_class_n}">N</span>
            <span class="gear-item {gear_class_d}">D</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if df_results.empty:
    st.error("暫未獲取到市場數據，請檢查網絡連線或點擊側邊欄重新掃描。")
    st.stop()

# 警報橫幅
perfect_matches = df_results[df_results['All_Rules_Met'] == True] if ('All_Rules_Met' in df_results.columns) else pd.DataFrame()
if not perfect_matches.empty:
    alert_symbols = ", ".join(perfect_matches['Symbol'].tolist())
    st.markdown(f"""
    <div class="alert-tesla">
        <div style="font-size:15px; font-weight:800; color:#FF4D4D;">
            🚨 OPTIMUS 實時強勢異動觸發！完美符合 J LAW 核心買點與主力吸籌：<span style="color:#FFF; font-size:17px;">{alert_symbols}</span>
        </div>
        <div style="font-size:11.5px; color:#E2E8F0; margin-top:4px;">
            達成標準：Stage 2 完美多頭 · RS 評級 ≥ 80 · 主力 CMF 淨流入 / Pocket Pivot · 距離買入點 ≤ 3%！
        </div>
    </div>
    """, unsafe_allow_html=True)

# 導航選擇
nav_selection = st.radio(
    "導航模式",
    [
        "🌐 大市宏觀與主力出貨日 (Market Telemetry)",
        "🌊 個股資金面異動雷達 (Smart Money Flow)",
        "🛡️ 核心持倉實戰情報 (Core Portfolio)",
        "01 // ⚡ 領頭羊即時機會庫 (M.E.T.A. Screener)",
        "02 // 🔍 7 維技術診斷與畫圖圖表 (Deep Radar & Drawing)",
        "03 // 🎯 1% 風險下單與金字塔加倉 (Execution & Pyramiding)"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# ----------------------------------------------------
# 模組 1: 大市宏觀與主力出貨日
# ----------------------------------------------------
if nav_selection == "🌐 大市宏觀與主力出貨日 (Market Telemetry)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            🌐 每日大市宏觀體檢 • 主力出貨日 (Distribution Days) 與電池總曝險計
        </h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:2px;">
            J Law / 歐奈爾經典法則：若大盤在 25 日內累積超過 5 個出貨日（跌 >0.2% 且放量），代表主力資金正在不計代價派發。
        </div>
    </div>
    """, unsafe_allow_html=True)

    dist_col1, dist_col2, dist_col3 = st.columns(3)
    with dist_col1:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color: {'#EF4444' if qqq_dist_days>=5 else '#10B981'};">
            <div class="hud-title">QQQ 納指主力出貨日 (25D)</div>
            <div class="hud-val" style="color: {'#EF4444' if qqq_dist_days>=5 else '#34D399'};">{qqq_dist_days} <span style="font-size:13px; color:#94A3B8;">天 {'(危險！主力派發中)' if qqq_dist_days>=5 else '(流動性安全)'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with dist_col2:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color: {'#EF4444' if spy_dist_days>=5 else '#10B981'};">
            <div class="hud-title">SPY 標普主力出貨日 (25D)</div>
            <div class="hud-val" style="color: {'#EF4444' if spy_dist_days>=5 else '#34D399'};">{spy_dist_days} <span style="font-size:13px; color:#94A3B8;">天 {'(拋壓沉重)' if spy_dist_days>=5 else '(流動性安全)'}</span></div>
        </div>
        """, unsafe_allow_html=True)
    with dist_col3:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color: {'#10B981' if recommended_exposure>=80 else ('#F59E0B' if recommended_exposure>=40 else '#EF4444')};">
            <div class="hud-title">🔋 BATTERY 建議總持倉上限</div>
            <div class="hud-val" style="color: {'#34D399' if recommended_exposure>=80 else ('#FACC15' if recommended_exposure>=40 else '#EF4444')};">{recommended_exposure}% <span style="font-size:13px; color:#94A3B8;">(當前檔位: {gear_text[:1]})</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    dia_df = indexes.get('DIA')
    col_idx1, col_idx2, col_idx3 = st.columns(3)

    def display_index_panel(sym, title, df, col):
        if df is None or len(df) < 50:
            col.info(f"{sym} 數據加載中...")
            return
        c = df['Close']
        curr, prev = float(c.iloc[-1]), float(c.iloc[-2])
        chg = ((curr - prev) / prev) * 100
        ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
        sma50 = float(c.rolling(50).mean().iloc[-1])
        sma200 = float(c.rolling(200).mean().iloc[-1]) if len(c) >= 200 else sma50
        atr14 = float((df['High'] - df['Low']).rolling(14).mean().iloc[-1])
        r1, s1 = curr + atr14, curr - atr14
        status_tag = "Stage 2 多頭" if curr > ema20 and ema20 > sma50 else "測試支撐"
        b_color = "badge-green" if curr > ema20 else "badge-gold"

        with col:
            st.markdown(f"""
            <div class="cyber-card" style="min-height:auto;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:800; font-size:16px; color:#FFF;">{sym} · {title}</span>
                    <span class="badge {b_color}">{status_tag}</span>
                </div>
                <div style="font-size:26px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0; color:#FFF;">
                    ${curr:.2f} <span style="font-size:15px; color:{'#10B981' if chg>=0 else '#EF4444'};">({'+' if chg>=0 else ''}{chg:.2f}%)</span>
                </div>
                <div style="font-size:12px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.7;">
                    • 20 EMA: <b style="color:#FFF;">${ema20:.2f}</b><br>
                    • 50 SMA: <b style="color:#FFF;">${sma50:.2f}</b> | 200 SMA: <b style="color:#FFF;">${sma200:.2f}</b><br>
                    • 阻力 (R1): <b style="color:#38BDF8;">${r1:.2f}</b> | 支撐 (S1): <b style="color:#EF4444;">${s1:.2f}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

    display_index_panel("QQQ", "納斯達克 100", qqq_df, col_idx1)
    display_index_panel("SPY", "標普 500", spy_df, col_idx2)
    display_index_panel("DIA", "道瓊斯工業", dia_df, col_idx3)

# ----------------------------------------------------
# 模組 2: 個股資金面異動雷達 (Smart Money Flow)
# ----------------------------------------------------
elif nav_selection == "🌊 個股資金面異動雷達 (Smart Money Flow)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            🌊 SMART MONEY FLOW • 美股個股資金面異動與機構吸籌雷達
        </h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:2px;">
            即時搜尋全池股票的主力大單蹤跡：聚焦 20日 CMF 資金流量、機構口袋買點 (Pocket Pivot) 與 50日多空攻防比。
        </div>
    </div>
    """, unsafe_allow_html=True)

    flow_filter = st.radio("資金異動維度快速篩選：", ["全部標的", "🔥 只睇主力強勢吸籌 (CMF > 0.15)", "⚡ 只睇觸發 Pocket Pivot (口袋買點)"], horizontal=True)

    df_flow = df_results.copy()
    if flow_filter == "🔥 只睇主力強勢吸籌 (CMF > 0.15)":
        df_flow = df_flow[df_flow['CMF'] > 0.15]
    elif flow_filter == "⚡ 只睇觸發 Pocket Pivot (口袋買點)":
        df_flow = df_flow[df_flow['Pocket_Pivot'] == "🔥 觸發"]

    st.dataframe(
        df_flow[['Symbol', 'Price', 'Change', 'Flow_Status', 'CMF', 'Pocket_Pivot', 'UpDown_Ratio', 'RVOL', 'RS', 'Score', 'Setup_Type']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Symbol": st.column_config.TextColumn("代碼"),
            "Price": st.column_config.NumberColumn("最新價 ($)", format="$%.2f"),
            "Change": st.column_config.NumberColumn("今日漲跌 (%)", format="%.2f%%"),
            "Flow_Status": st.column_config.TextColumn("主力資金狀態"),
            "CMF": st.column_config.NumberColumn("20D 蔡金資金流", format="%.2f"),
            "Pocket_Pivot": st.column_config.TextColumn("Pocket Pivot 口袋買點"),
            "UpDown_Ratio": st.column_config.NumberColumn("50D 多空量能比", format="%.2fx"),
            "RVOL": st.column_config.NumberColumn("量比", format="%.2fx"),
            "RS": st.column_config.ProgressColumn("RS 強度", min_value=1, max_value=99, format="%d"),
            "Score": st.column_config.ProgressColumn("J Law 評分", min_value=0, max_value=100, format="%d"),
            "Setup_Type": st.column_config.TextColumn("型態")
        }
    )

# ----------------------------------------------------
# 模組 3: 核心持倉實戰情報
# ----------------------------------------------------
elif nav_selection == "🛡️ 核心持倉實戰情報 (Core Portfolio)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            🛡️ 核心持倉實戰情報 (TSLA · AAOI · NVDA · MU · BE · NBIS · DDOG)
        </h4>
    </div>
    """, unsafe_allow_html=True)

    df_core = df_results[df_results['Symbol'].isin(CORE_PORTFOLIO_SYMBOLS)].copy()
    if not df_core.empty:
        st.dataframe(
            df_core[['Symbol', 'Rank', 'Price', 'Change', 'RS', 'Score', 'Flow_Status', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R', 'RVOL']],
            use_container_width=True,
            hide_index=True,
            column_config=GRID_COLUMN_CONFIG
        )

# ----------------------------------------------------
# 模組 4: 領頭羊即時機會庫
# ----------------------------------------------------
elif nav_selection == "01 // ⚡ 領頭羊即時機會庫 (M.E.T.A. Screener)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            01 // ⚡ M.E.T.A. SCREENER • J LAW 領頭羊即時機會庫
        </h4>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="hud-telemetry">
            <div class="hud-title">SCAN UNIVERSE</div>
            <div class="hud-val">{len(df_results)} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color:#06B6D4;">
            <div class="hud-title">💎 DIAMOND ALPHA</div>
            <div class="hud-val" style="color:#22D3EE;">{len(df_results[df_results['Rank'] == 'Diamond'])} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color:#FACC15;">
            <div class="hud-title">🥇 GOLD TIER</div>
            <div class="hud-val" style="color:#FACC15;">{len(df_results[df_results['Rank'] == 'Gold'])} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="hud-telemetry" style="border-left-color:#A855F7;">
            <div class="hud-title">🔥 主力吸籌股數</div>
            <div class="hud-val" style="color:#C084FC;">{len(df_results[df_results['CMF'] > 0.1])} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    f_c1, f_c2 = st.columns([1.5, 2.5])
    with f_c1:
        filter_tier = st.selectbox("🎯 評級篩選", ["全部評級", "只睇 💎 Diamond", "只睇 💎 Diamond + 🥇 Gold"], index=0)
    with f_c2:
        only_near_entry = st.checkbox("🎯 只顯示現價距離買入點 ≤ 3%（隨時可啟動）", value=False)

    df_filtered = df_results.copy()
    if filter_tier == "只睇 💎 Diamond":
        df_filtered = df_filtered[df_filtered['Rank'] == 'Diamond']
    elif filter_tier == "只睇 💎 Diamond + 🥇 Gold":
        df_filtered = df_filtered[df_filtered['Rank'].isin(['Diamond', 'Gold'])]

    if only_near_entry:
        df_filtered = df_filtered[df_filtered['Entry_Diff'].abs() <= 3.0]

    display_cards = df_filtered.head(4)
    if not display_cards.empty:
        card_cols = st.columns(len(display_cards))
        for i, (_, row_q) in enumerate(display_cards.iterrows()):
            b_class = "badge-diamond" if row_q['Rank'] == 'Diamond' else "badge-gold"
            with card_cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="badge {b_class}">{row_q['Rank']} TIER</span>
                            <span style="font-family:'JetBrains Mono'; font-weight:700; color:#38BDF8; font-size:12px;">★ {row_q['Edges']} 重優勢</span>
                        </div>
                        <div style="font-size:24px; font-weight:800; font-family:'JetBrains Mono'; margin:6px 0 2px 0; color:#FFF;">
                            {row_q['Symbol']}
                        </div>
                        <div style="font-size:15px; font-family:'JetBrains Mono'; font-weight:600; color:{'#10B981' if row_q['Change'] >= 0 else '#EF4444'};">
                            ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
                        </div>
                        <div style="margin-top:4px;">
                            <span class="badge badge-flow">CMF {row_q['CMF']}</span>
                            {f'<span class="badge badge-green">POCKET PIVOT</span>' if row_q['Pocket_Pivot']=='🔥 觸發' else ''}
                        </div>
                    </div>
                    <div style="margin-top:10px; font-size:11.5px; color:#CBD5E1; font-family:'JetBrains Mono'; line-height:1.6; border-top:1px solid rgba(255,255,255,0.06); padding-top:8px;">
                        型態: <span style="color:#38BDF8;">{row_q['Setup_Type']}</span><br>
                        樞紐買點: <b style="color:#FFF;">${row_q['Entry']:.2f}</b><br>
                        防守止損: <b style="color:#EF4444;">${row_q['Stop']:.2f} ({row_q['Stop_Pct']}%)</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("當前條件下暫無符合的標的。")

    with st.expander("📋 展開查看完整合格標的清單與量化指標", expanded=True):
        st.dataframe(
            df_filtered[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Flow_Status', 'CMF', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
            use_container_width=True,
            hide_index=True,
            column_config=GRID_COLUMN_CONFIG
        )

    st.write("")
    symbols_tv_format = ", ".join([f"{s}" for s in df_filtered['Symbol'].tolist()])
    with st.expander("📤 一鍵匯出篩選結果 (TradingView / 富途牛牛 Watchlist 格式)"):
        st.caption("複製下方代碼，可直接貼入 TradingView 自選監控列表：")
        st.code(symbols_tv_format, language="text")

# ----------------------------------------------------
# 模組 5: 7 維技術診斷與專業畫圖
# ----------------------------------------------------
elif nav_selection == "02 // 🔍 7 維技術診斷與畫圖圖表 (Deep Radar & Drawing)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            02 // 🔍 DEEP RADAR • 7 維技術形態診斷與 TRADINGVIEW 專業畫圖圖表
        </h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:2px;">
            左側工具列已解鎖：趨勢線、阻力支撐箱體、盈虧比測算標尺；右上角支援切換週期及直接更換股票代碼。
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_stock = st.selectbox("🎯 選擇要深度診斷的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == selected_stock].iloc[0]

    c_r1, c_r2 = st.columns([1.05, 1.95])

    with c_r1:
        st.markdown(f"#### 📋 **{selected_stock}** J Law 7 維檢核")
        checklist = [
            ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "符合", "股價 > 50SMA > 150SMA > 200SMA，均線向上排開。"),
            ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS 為 {stock_row['RS']} 分，跑贏市場 80% 以上股票。"),
            ("3. VCP 波動收窄蓄勢", any("VCP" in r for r in stock_row['Reasons']), "ATR 波幅收斂，籌碼在樞紐區沉澱。"),
            ("4. 主力資金與 Pocket Pivot", stock_row['CMF'] > 0.05 or stock_row['Pocket_Pivot'] == "🔥 觸發", f"CMF 為 {stock_row['CMF']}，狀態：{stock_row['Flow_Status']}。"),
            ("5. 20 EMA 動態支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距 20 EMA 僅 {stock_row['Dist_20EMA']}%，處於黃金回踩買區。"),
            ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"相對量比 (RVOL) 為 {stock_row['RVOL']}x。"),
            ("7. 結構點位設定", True, f"型態為「{stock_row['Setup_Type']}」，規劃買點 ${stock_row['Entry']:.2f}。")
        ]
        for title, passed, desc in checklist:
            s_icon = "✅" if passed else "⚠️"
            b_color = "#10B981" if passed else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(14, 19, 31, 0.85); border-left:3px solid {b_color}; padding:8px 12px; margin-bottom:8px; border-radius:4px;">
                <div style="font-weight:700; color:#FFF; font-size:13px;">{s_icon} {title}</div>
                <div style="font-size:11.5px; color:#94A3B8; margin-top:2px;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with c_r2:
        tv_code = f"""
        <div class="tradingview-widget-container" style="height:550px;width:100%;">
          <div id="tv_advanced_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{selected_stock}",
            "interval": "D",
            "timezone": "America/New_York",
            "theme": "dark",
            "style": "1",
            "locale": "zh_TW",
            "toolbar_bg": "#0B0E14",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "save_image": true,
            "withdateranges": true,
            "studies": [
              "MASimple@tv-basicstudies",
              "EMA@tv-basicstudies"
            ],
            "container_id": "tv_advanced_{selected_stock}"
          }});
          </script>
        </div>
        """
        components.html(tv_code, height=560)

# ----------------------------------------------------
# 模組 6: 1% 風險下單與金字塔加倉
# ----------------------------------------------------
elif nav_selection == "03 // 🎯 1% 風險下單與金字塔加倉 (Execution & Pyramiding)":
    st.markdown("""
    <div class="section-header">
        <h4 style="margin:0; color:#FFF; font-weight:800;">
            03 // 🎯 EXECUTION & PYRAMIDING • 1% 倉位精算與 J LAW 冠軍金字塔加倉引擎
        </h4>
        <div style="font-size:12px; color:#94A3B8; margin-top:2px;">
            J Law 冠軍鐵律：絕不逆勢攤平！僅在首注獲利拉開後，於次級突破點進行 50% $\rightarrow$ 30% $\rightarrow$ 20% 右側加碼。
        </div>
    </div>
    """, unsafe_allow_html=True)

    target_calc_sym = st.selectbox("選擇計算下單標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == target_calc_sym].iloc[0]

    inp_c1, inp_c2, inp_c3 = st.columns(3)
    with inp_c1:
        account_capital = st.number_input("賬戶總資產 ($)", min_value=1000, max_value=10000000, value=50000, step=5000)
    with inp_c2:
        risk_pct = st.slider("單筆最大承受風險 (%)", min_value=0.5, max_value=2.5, value=1.0, step=0.1)
    with inp_c3:
        max_pos_cap = st.slider("單一持倉上限 (%)", min_value=10, max_value=40, value=25, step=5)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    target_entry = stock_row['Entry']
    target_stop = stock_row['Stop']
    target_risk_per_share = stock_row['Risk_Per_Share']
    target_stop_pct = stock_row['Stop_Pct']
    target_2r = stock_row['Target_2R']
    target_3r = stock_row['Target_3R']

    calc_shares = int(max_risk_dollars / target_risk_per_share) if target_risk_per_share > 0 else 0
    total_pos_cost = calc_shares * target_entry
    max_allowed_cost = account_capital * (max_pos_cap / 100.0)
    
    adj_msg = ""
    if total_pos_cost > max_allowed_cost:
        calc_shares = int(max_allowed_cost / target_entry)
        total_pos_cost = calc_shares * target_entry
        adj_msg = f"⚠️ 受限於持倉上限 ({max_pos_cap}%)，股數已自動限制為安全額度。"

    pos_pct_of_capital = (total_pos_cost / account_capital) * 100

    plan_c1, plan_c2 = st.columns(2)

    with plan_c1:
        st.markdown(f"""
        <div class="action-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h4 style="margin:0; color:#38BDF8;">🎯 {target_calc_sym} 結構進出場點位</h4>
                <span class="badge badge-tesla">{stock_row['Setup_Type']}</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(2, 1fr); gap: 10px;">
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🔵 樞紐進場 (Entry):</span><br>
                    <b style="font-size:20px; color:#38BDF8;">${target_entry:.2f}</b><br>
                    <span style="font-size:10.5px; color:#CBD5E1;">現價: ${stock_row['Price']:.2f}</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🔴 結構止損 (Stop):</span><br>
                    <b style="font-size:20px; color:#EF4444;">${target_stop:.2f} ({target_stop_pct}%)</b><br>
                    <span style="font-size:10.5px; color:#EF4444;">每股風險: ${target_risk_per_share:.2f}</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🟢 趁強賣出 (2R 鎖利):</span><br>
                    <b style="font-size:20px; color:#10B981;">${target_2r:.2f}</b><br>
                    <span style="font-size:10.5px; color:#6EE7B7;">平半倉 + 止損移至成本</span>
                </div>
                <div style="background:rgba(255,255,255,0.04); padding:10px; border-radius:6px;">
                    <span style="color:#94A3B8; font-size:11.5px;">🌟 趁弱賣出 (3R+ 移停):</span><br>
                    <b style="font-size:20px; color:#F59E0B;">${target_3r:.2f}</b><br>
                    <span style="font-size:10.5px; color:#FCD34D;">沿 20 EMA 騎乘主升浪</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with plan_c2:
        st.markdown(f"""
        <div class="action-box" style="border-color: rgba(16, 185, 129, 0.4);">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h4 style="margin:0; color:#10B981;">🛡️ 1% 風險倉位精算</h4>
                <span class="badge badge-green">風控鎖定</span>
            </div>
            <div style="line-height:1.9; font-size:13.5px;">
                • 賬戶總額: <b>${account_capital:,.2f}</b><br>
                • 最大承擔虧損 (1R): <b style="color:#EF4444;">${max_risk_dollars:,.2f}</b> ({risk_pct}%)<br>
                • 每股承擔風險: <b>${target_risk_per_share:.2f}</b><br>
                <hr style="border:0; border-top:1px solid rgba(255,255,255,0.08); margin:8px 0;">
                • <b>推薦進場股數:</b> <span style="font-size:22px; color:#10B981; font-weight:800;">{calc_shares} 股</span><br>
                • <b>預計持倉成本:</b> <b>${total_pos_cost:,.2f}</b> ({pos_pct_of_capital:.1f}% 倉位)<br>
                • <b>觸發止損總虧損:</b> <b style="color:#EF4444;">-${calc_shares * target_risk_per_share:,.2f}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if adj_msg:
        st.info(adj_msg)

    st.write("")
    st.markdown("#### ⚡ J Law 右側金字塔加倉模型 (Pyramiding Execution Plan)")
    base_shares = int(calc_shares * 0.5)
    add1_shares = int(calc_shares * 0.3)
    add2_shares = int(calc_shares * 0.2)
    add1_est_price = round(target_entry * 1.04, 2)
    add2_est_price = round(target_entry * 1.08, 2)
    avg_price_after_add1 = round(((base_shares * target_entry) + (add1_shares * add1_est_price)) / (base_shares + add1_shares), 2) if (base_shares + add1_shares) > 0 else 0

    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        st.markdown(f"""
        <div style="background:rgba(14,19,31,0.85); border:1px solid rgba(255,255,255,0.08); padding:12px; border-radius:6px;">
            <span class="badge badge-cyan">第 1 注：底倉 (50%)</span>
            <div style="font-size:18px; font-weight:800; color:#FFF; margin:6px 0;">{base_shares} 股 @ ${target_entry:.2f}</div>
            <div style="font-size:11.5px; color:#94A3B8;">初始結構買點進場，止損設在 ${target_stop:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col2:
        st.markdown(f"""
        <div style="background:rgba(14,19,31,0.85); border:1px solid rgba(255,255,255,0.08); padding:12px; border-radius:6px;">
            <span class="badge badge-gold">第 2 注：次級加倉 (30%)</span>
            <div style="font-size:18px; font-weight:800; color:#FFF; margin:6px 0;">{add1_shares} 股 @ ~${add1_est_price:.2f}</div>
            <div style="font-size:11.5px; color:#94A3B8;">底倉浮盈時加碼，加倉後均價約 ${avg_price_after_add1:.2f}，止損上移至保本價</div>
        </div>
        """, unsafe_allow_html=True)
    with p_col3:
        st.markdown(f"""
        <div style="background:rgba(14,19,31,0.85); border:1px solid rgba(255,255,255,0.08); padding:12px; border-radius:6px;">
            <span class="badge badge-green">第 3 注：主升追加 (20%)</span>
            <div style="font-size:18px; font-weight:800; color:#FFF; margin:6px 0;">{add2_shares} 股 @ ~${add2_est_price:.2f}</div>
            <div style="font-size:11.5px; color:#94A3B8;">確認龍頭地位，全倉改為 10/20 EMA 移動止損</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    order_script = (
        f"【富途 / IB 下單草稿 - {target_calc_sym}】\n"
        f"買入指令: 限價單 (Limit) @ ${target_entry:.2f} | 數量: {calc_shares} 股\n"
        f"條件止損: 止損單 (Stop Loss) @ ${target_stop:.2f}\n"
        f"止盈目標: 2R 趁強平半 @ ${target_2r:.2f} (半倉: {calc_shares // 2} 股) | 3R 移停 @ ${target_3r:.2f}"
    )
    st.text_area("📋 券商下單指令草稿 (可直接複製至交易筆記或券商下單窗口)", value=order_script, height=105)
