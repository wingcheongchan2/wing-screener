import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import datetime

# ==========================================
# 0. 系統核心配置
# ==========================================
st.set_page_config(
    page_title="TESLA OS // J LAW ALPHA TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 1. 旗艦級 TESLA OS 視覺引擎 (雙層暗影遮罩 + 毛玻璃卡片)
# ==========================================
def inject_pure_tesla_os():
    # 預設使用 Tesla 官方/高畫質車隊產品大合照 (S/3/X/Y/Cybertruck/Semi/Cybercab/Optimus)
    # 如有自己的本地圖片，可將 url 改為相對路徑或 base64
    tesla_bg_url = "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=2560&q=85"

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* 全局重置與 Tesla 全產品背景圖 (多重遮罩確保文字 100% 清晰) */
        .block-container {{
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 96% !important;
        }}

        .stApp {{
            background-color: #07090E !important;
            background-image: 
                radial-gradient(circle at 50% 10%, rgba(232, 33, 39, 0.12) 0%, transparent 45%),
                linear-gradient(180deg, rgba(7, 9, 14, 0.82) 0%, rgba(7, 9, 14, 0.94) 50%, #07090E 100%),
                url("{tesla_bg_url}") !important;
            background-size: cover !important;
            background-position: center top !important;
            background-attachment: fixed !important;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
            letter-spacing: -0.01em;
        }}

        /* Cybertruck 貫穿式前燈冷光飾條 */
        .cyber-lightbar {{
            height: 2px;
            width: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(232, 33, 39, 0.8) 25%, #FFFFFF 50%, rgba(232, 33, 39, 0.8) 75%, transparent 100%);
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.5);
            margin-bottom: 14px;
        }}

        /* Tesla 車機頂部狀態控制條 (毛玻璃懸浮) */
        .tesla-top-nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(13, 17, 24, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px 20px;
            margin-bottom: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
        }}

        /* 屏幕 PRND 換檔組件 */
        .gear-console {{
            display: inline-flex;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 2px;
            gap: 2px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 800;
        }}
        .gear-pill {{
            padding: 4px 10px;
            border-radius: 4px;
            color: #475569;
        }}
        .gear-active-d {{ background: #10B981; color: #042F2E !important; }}
        .gear-active-n {{ background: #F59E0B; color: #451A03 !important; }}
        .gear-active-p {{ background: #E82127; color: #FFFFFF !important; }}

        /* 遙測數據指標卡片 (4格微透明 HUD) */
        .telemetry-deck {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin-bottom: 18px;
        }}
        .telemetry-node {{
            background: rgba(14, 19, 28, 0.82);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-top: 2px solid rgba(255, 255, 255, 0.16);
            border-radius: 8px;
            padding: 14px 18px;
            transition: all 0.25s ease;
        }}
        .telemetry-node:hover {{
            border-top-color: #E82127;
            background: rgba(18, 25, 38, 0.9);
            transform: translateY(-2px);
        }}
        .telemetry-tag {{
            font-size: 11px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.6px;
            text-transform: uppercase;
        }}
        .telemetry-val {{
            font-size: 24px;
            font-weight: 800;
            color: #FFFFFF;
            font-family: 'JetBrains Mono', monospace;
            margin: 6px 0 2px 0;
        }}
        .telemetry-sub {{
            font-size: 11px;
            color: #64748B;
            font-family: 'Inter', sans-serif;
        }}

        /* 車機觸控 Dock (st.tabs 精緻化) */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px !important;
            background: rgba(10, 14, 22, 0.85) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 6px !important;
            border-radius: 8px !important;
            margin-bottom: 18px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: transparent !important;
            border: none !important;
            border-radius: 6px !important;
            padding: 9px 20px !important;
            color: #94A3B8 !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.05) !important;
        }}
        .stTabs [aria-selected="true"] {{
            background: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 12px rgba(232, 33, 39, 0.45) !important;
        }}

        /* 核心股票裝甲卡片 (分層架構、高清晰對比) */
        .cyber-card {{
            background: rgba(13, 18, 27, 0.84);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 215px;
            transition: all 0.25s ease;
        }}
        .cyber-card:hover {{
            border-color: rgba(232, 33, 39, 0.8);
            background: rgba(17, 23, 35, 0.92);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        }}

        /* 半透明微標籤 (收斂色彩，杜絕實色膠囊) */
        .badge {{
            display: inline-flex;
            align-items: center;
            white-space: nowrap !important;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.4px;
        }}
        .b-diamond {{ background: rgba(56, 189, 248, 0.12); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); }}
        .b-gold {{ background: rgba(245, 158, 11, 0.12); color: #FBBF24; border: 1px solid rgba(245, 158, 11, 0.3); }}
        .b-green {{ background: rgba(16, 185, 129, 0.14); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.35); }}
        .b-red {{ background: rgba(232, 33, 39, 0.14); color: #F87171; border: 1px solid rgba(232, 33, 39, 0.4); }}
        .b-purple {{ background: rgba(168, 85, 247, 0.14); color: #C084FC; border: 1px solid rgba(168, 85, 247, 0.35); }}

        /* 警報橫幅 (暗調左飾條) */
        .tesla-alert {{
            background: rgba(232, 33, 39, 0.08);
            backdrop-filter: blur(12px);
            border-left: 3px solid #E82127;
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: #CBD5E1;
        }}

        #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 標的池配置
# ==========================================
CORE_PORTFOLIO_SYMBOLS = ["TSLA", "AAOI", "NVDA", "MU", "BE", "NBIS", "DDOG"]

DEFAULT_UNIVERSE = list(dict.fromkeys(CORE_PORTFOLIO_SYMBOLS + [
    "AAPL", "MSFT", "AMZN", "META", "GOOGL", "AMD", "AVGO", "ARM", "QCOM", "TSM", "ASML", 
    "LRCX", "KLAC", "SMCI", "MRVL", "PLTR", "MSTR", "COIN", "CRWD", "PANW", "NET", "SNOW", 
    "NOW", "SHOP", "APP", "CVNA", "UPST", "TTD", "SE", "MELI", "CEG", "VST", "GE", "CAT", 
    "LLY", "ISRG", "COST", "NFLX", "UBER", "ABNB", "HOOD", "SOFI", "DKNG", "CELH", "ONON"
]))

# ==========================================
# 3. 數據下載引擎
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
            return df if len(df) >= 100 else None
        except Exception:
            return None

    df_spy = extract_clean_df(data, 'SPY')
    df_qqq = extract_clean_df(data, 'QQQ')
    df_dia = extract_clean_df(data, 'DIA')
    stocks = {s: extract_clean_df(data, s) for s in tickers if extract_clean_df(data, s) is not None}
    return stocks, df_spy, df_qqq, df_dia

def calculate_distribution_days(df, lookback=25):
    if df is None or len(df) < lookback + 1: return 0
    recent = df.iloc[-lookback:].copy()
    prev_close = df['Close'].shift(1).iloc[-lookback:]
    prev_vol = df['Volume'].shift(1).iloc[-lookback:]
    is_dist = (recent['Close'] < prev_close * 0.998) & (recent['Volume'] > prev_vol)
    return int(is_dist.sum())

# ==========================================
# 4. J Law M.E.T.A. 結構量化定價演算法
# ==========================================
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

        # 資金面：20D CMF
        hl_diff = (h - l).replace(0, 1e-9)
        mf_multiplier = ((c - l) - (h - c)) / hl_diff
        mf_volume = mf_multiplier * v
        cmf_20 = float(mf_volume.rolling(20).sum().iloc[-1] / v.rolling(20).sum().replace(0, 1e-9).iloc[-1])
        
        # Pocket Pivot (機構口袋買點)
        is_up_today = curr_price > prev_price
        last_10_down_vol = [v.iloc[-(i+1)] for i in range(1, 11) if c.iloc[-(i+1)] < c.iloc[-(i+2)]]
        max_down_vol = max(last_10_down_vol) if last_10_down_vol else 0
        is_pocket_pivot = is_up_today and (v.iloc[-1] > max_down_vol) and (curr_price >= ema10 * 0.98)

        if cmf_20 > 0.15 or (is_pocket_pivot and cmf_20 > 0.05):
            flow_status = "🔥 主力吸籌"
            score += 15
            reasons.append("主力淨流入")
        elif cmf_20 < -0.10:
            flow_status = "⚠️ 資金派發"
            score -= 10
        else:
            flow_status = "⚖️ 資金中性"

        if is_pocket_pivot:
            score += 10
            meta_edges += 1
            reasons.append("觸發口袋買點")

        # Stage 2 範式
        is_stage2 = False
        if curr_price > sma50 and sma50 > sma150 and sma150 > sma200:
            score += 20
            if sma200 >= sma200_20d_ago and dist_h52 >= -25.0 and dist_l52 >= 25.0:
                is_stage2 = True
                meta_edges += 1
                reasons.append("Stage 2 完美多頭")
        elif curr_price > sma50:
            score += 8

        # RS 相對強度
        def perf(series, days):
            d = min(len(series) - 1, days)
            return (series.iloc[-1] / series.iloc[-d]) - 1

        stock_w = 0.4 * perf(c, 63) + 0.3 * perf(c, 126) + 0.3 * perf(c, min(252, len(c)-1))
        spy_w = 0.4 * perf(df_spy['Close'], 63) + 0.3 * perf(df_spy['Close'], 126) + 0.3 * perf(df_spy['Close'], 252)
        rs_rating = int(np.clip(50 + ((stock_w - spy_w) * 100 * 1.5), 1, 99))

        if rs_rating >= 80:
            score += 25
            meta_edges += 1
            reasons.append(f"領頭羊 (RS {rs_rating})")
        elif rs_rating >= 65:
            score += 15
        elif rs_rating >= 50: score += 8

        # VCP 波動收窄
        tr = pd.concat([h - l, (h - c.shift(1)).abs(), (l - c.shift(1)).abs()], axis=1).max(axis=1)
        atr14 = float(tr.rolling(14).mean().iloc[-1])
        atr50 = float(tr.rolling(50).mean().iloc[-1])
        is_vcp = False
        if (atr14 / (atr50 if atr50 > 0 else 1)) <= 0.85:
            score += 12
            is_vcp = True
            meta_edges += 1
            reasons.append("VCP 波動收窄")
        if float(c.iloc[-5:].std() / curr_price) < 0.025:
            score += 5
            reasons.append("緊密收市")

        # 均線回踩
        dist_ema10 = ((curr_price - ema10) / ema10) * 100
        dist_ema20 = ((curr_price - ema20) / ema20) * 100
        is_ma_support = False
        if 0 <= dist_ema20 <= 2.5 or 0 <= dist_ema10 <= 2.0:
            score += 15
            is_ma_support = True
            meta_edges += 1
            reasons.append("回踩 10/20 EMA")
        elif -2.0 <= dist_ema20 < 0:
            score += 8

        # DRSI 動能
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
            drsi_status = "超賣金叉" if k_val < 35 else "多頭金叉"
            score += 12
            reasons.append(f"DRSI {drsi_status}")
        elif k_val > d_val:
            score += 6
            drsi_status = "多頭維持"

        # 量比 RVOL
        v_50 = float(v.rolling(50).mean().iloc[-1])
        rvol = float(v.iloc[-1]) / (v_50 if v_50 > 0 else 1)
        if change_pct > 0 and rvol >= 1.3:
            score += 10
            reasons.append(f"爆量 ({rvol:.1f}x)")
        elif rvol < 0.75:
            score += 7
            reasons.append("量縮沉澱 (VDU)")

        total_score = int(np.clip(score, 0, 100))
        rank = "Diamond" if (total_score >= 80 and is_stage2) else ("Gold" if total_score >= 65 else ("Silver" if total_score >= 50 else "Bronze"))

        # 結構定價計算
        recent_10d_high = float(h.iloc[-10:].max())
        recent_10d_low = float(l.iloc[-10:].min())

        if is_ma_support or abs(dist_ema20) <= 2.5:
            setup_type = "M.E.T.A. 回踩買點"
            calc_entry = round(max(ema20, curr_price) * 1.002, 2)
            calc_stop = round(min(ema20 * 0.965, calc_entry - (1.5 * atr14)), 2)
        else:
            setup_type = "VCP 樞紐突破點"
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
            "All_Rules_Met": is_all_rules_met,
            "Reasons": reasons
        }
    except Exception:
        return None

# ==========================================
# 5. 主應用渲染
# ==========================================
inject_pure_tesla_os()

# 抓取市場數據
stock_dict, df_spy, df_qqq, df_dia = fetch_all_data(DEFAULT_UNIVERSE)
results = [evaluate_jlaw_stock(sym, df_t, df_spy) for sym, df_t in stock_dict.items()] if stock_dict and df_spy is not None else []
results = [r for r in results if r is not None]
df_results = pd.DataFrame(results)
if not df_results.empty:
    df_results = df_results.sort_values(by=['Score', 'RS'], ascending=[False, False]).reset_index(drop=True)

# 大盤指標計算
qqq_dist_days = calculate_distribution_days(df_qqq, lookback=25)
spy_dist_days = calculate_distribution_days(df_spy, lookback=25)

qqq_curr = float(df_qqq['Close'].iloc[-1]) if df_qqq is not None else 0
qqq_ema20 = float(df_qqq['Close'].ewm(span=20, adjust=False).mean().iloc[-1]) if df_qqq is not None else 0
spy_curr = float(df_spy['Close'].iloc[-1]) if df_spy is not None else 0
spy_sma50 = float(df_spy['Close'].rolling(50).mean().iloc[-1]) if df_spy is not None else 0

if (qqq_curr > qqq_ema20 and spy_curr > spy_sma50) and (qqq_dist_days < 5 and spy_dist_days < 5):
    gear_mode = "D"
    gear_text = "DRIVE (PLAID 滿油門)"
    recommended_exposure = 100
elif (qqq_curr > qqq_ema20 or spy_curr > spy_sma50) and (qqq_dist_days < 6):
    gear_mode = "N"
    gear_text = "NEUTRAL (STANDARD 輕倉)"
    recommended_exposure = 40
else:
    gear_mode = "P"
    gear_text = "PARK (CHILL 防禦防守)"
    recommended_exposure = 10

# 1. 貫穿式前燈飾條
st.markdown('<div class="cyber-lightbar"></div>', unsafe_allow_html=True)

# 2. 頂部狀態列
st.markdown(f"""
<div class="tesla-top-nav">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:16px; font-weight:800; font-family:'JetBrains Mono'; letter-spacing:1px; color:#FFF;">
            TESLA // CYBER TERMINAL
        </span>
        <span class="badge b-red">FSD V13.2</span>
        <span class="badge b-diamond">HW4.0 ACTIVE</span>
    </div>
    <div style="display:flex; align-items:center; gap:14px;">
        <span style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono';">{gear_text}</span>
        <div class="gear-console">
            <span class="gear-pill {'gear-active-p' if gear_mode=='P' else ''}">P</span>
            <span class="gear-pill">R</span>
            <span class="gear-pill {'gear-active-n' if gear_mode=='N' else ''}">N</span>
            <span class="gear-pill {'gear-active-d' if gear_mode=='D' else ''}">D</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 3. 遙測 HUD 模組
diamond_count = len(df_results[df_results['Rank'] == 'Diamond']) if not df_results.empty else 0
accum_count = len(df_results[df_results['CMF'] > 0.1]) if not df_results.empty else 0

st.markdown(f"""
<div class="telemetry-deck">
    <div class="telemetry-node">
        <div class="telemetry-tag">⚡ CYBERCAB • FSD ALPHA</div>
        <div class="telemetry-val" style="color:#38BDF8;">{diamond_count} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        <div class="telemetry-sub">Stage 2 多頭領頭羊</div>
    </div>
    <div class="telemetry-node">
        <div class="telemetry-tag">📐 CYBERTRUCK • 30X STEEL</div>
        <div class="telemetry-val" style="color:{'#34D399' if qqq_dist_days<5 else '#F87171'};">{qqq_dist_days} / 25 <span style="font-size:13px; color:#94A3B8;">天</span></div>
        <div class="telemetry-sub">納指派發日 ({'安全期' if qqq_dist_days<5 else '危險派發'})</div>
    </div>
    <div class="telemetry-node">
        <div class="telemetry-tag">🤖 OPTIMUS • NEURAL FLOW</div>
        <div class="telemetry-val" style="color:#C084FC;">{accum_count} <span style="font-size:13px; color:#94A3B8;">隻</span></div>
        <div class="telemetry-sub">CMF 主力吸籌 / 異動</div>
    </div>
    <div class="telemetry-node">
        <div class="telemetry-tag">🔋 POWERPACK • EXPOSURE</div>
        <div class="telemetry-val" style="color:{'#34D399' if recommended_exposure>=80 else ('#FBBF24' if recommended_exposure>=40 else '#F87171')};">{recommended_exposure}%</div>
        <div class="telemetry-sub">建議賬戶最大總曝險</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 警報橫幅
perfect_matches = df_results[df_results['All_Rules_Met'] == True] if ('All_Rules_Met' in df_results.columns) else pd.DataFrame()
if not perfect_matches.empty:
    alert_symbols = ", ".join(perfect_matches['Symbol'].tolist())
    st.markdown(f"""
    <div class="tesla-alert">
        🚨 <b>OPTIMUS 實時強勢異動觸發：</b> 符合 J LAW 7 大核心規則：<b style="color:#FFF;">{alert_symbols}</b>
        <span style="color:#94A3B8; margin-left:8px;">（Stage 2 多頭 · RS ≥ 80 · 主力吸籌 · 距買入點 ≤ 3%）</span>
    </div>
    """, unsafe_allow_html=True)

# 5. 車機觸控 Dock 欄
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "⚡ 領頭羊即時機會庫",
    "🌊 主力資金異動雷達",
    "🛡️ 核心持倉實戰情報",
    "📈 TradingView 專業畫圖",
    "🎯 1% 下單與金字塔加倉"
])

# ----------------------------------------------------
# TAB 1: 領頭羊機會庫
# ----------------------------------------------------
with tab1:
    f_c1, f_c2 = st.columns([1.2, 2.8])
    with f_c1:
        filter_tier = st.selectbox("評級篩選：", ["全部標的", "💎 只睇 Diamond", "💎 Diamond + 🥇 Gold"], index=0)
    with f_c2:
        only_near_entry = st.checkbox("🎯 只顯示現價距離買入點 ≤ 3%（隨時起爆）", value=False)

    df_filtered = df_results.copy()
    if filter_tier == "💎 只睇 Diamond":
        df_filtered = df_filtered[df_filtered['Rank'] == 'Diamond']
    elif filter_tier == "💎 Diamond + 🥇 Gold":
        df_filtered = df_filtered[df_filtered['Rank'].isin(['Diamond', 'Gold'])]

    if only_near_entry:
        df_filtered = df_filtered[df_filtered['Entry_Diff'].abs() <= 3.0]

    # 卡片展示 (重構資訊階層)
    display_cards = df_filtered.head(4)
    if not display_cards.empty:
        card_cols = st.columns(len(display_cards))
        for i, (_, row_q) in enumerate(display_cards.iterrows()):
            b_class = "b-diamond" if row_q['Rank'] == 'Diamond' else "b-gold"
            with card_cols[i]:
                st.markdown(f"""
                <div class="cyber-card">
                    <div>
                        <!-- Header: 代號與評級 -->
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span class="badge {b_class}">{row_q['Rank']} TIER</span>
                            <span style="font-family:'JetBrains Mono'; font-weight:700; color:#94A3B8; font-size:11px;">★ {row_q['Edges']} 重優勢</span>
                        </div>
                        <div style="font-size:24px; font-weight:800; font-family:'JetBrains Mono'; margin:8px 0 2px 0; color:#FFFFFF; letter-spacing:0.5px;">
                            {row_q['Symbol']}
                        </div>
                        <div style="font-size:15px; font-family:'JetBrains Mono'; font-weight:600; color:{'#34D399' if row_q['Change'] >= 0 else '#F87171'};">
                            ${row_q['Price']:.2f} ({'+' if row_q['Change']>0 else ''}{row_q['Change']:.2f}%)
                        </div>
                        <!-- 技術指標 Badges -->
                        <div style="margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;">
                            <span class="badge b-purple">CMF {row_q['CMF']}</span>
                            {f'<span class="badge b-green">POCKET PIVOT</span>' if row_q['Pocket_Pivot']=='🔥 觸發' else ''}
                        </div>
                    </div>
                    <!-- 底部風控與點位區域 -->
                    <div style="margin-top:14px; font-size:11px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.7; border-top:1px solid rgba(255,255,255,0.07); padding-top:10px;">
                        <span style="color:#64748B;">型態:</span> <span style="color:#E2E8F0;">{row_q['Setup_Type']}</span><br>
                        買入: <b style="color:#FFFFFF;">${row_q['Entry']:.2f}</b> │ 止損: <b style="color:#F87171;">${row_q['Stop']:.2f} ({row_q['Stop_Pct']}%)</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with st.expander("📋 展開完整合格清單", expanded=True):
        st.dataframe(
            df_filtered[['Symbol', 'Rank', 'Score', 'Price', 'Change', 'RS', 'Flow_Status', 'CMF', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
            use_container_width=True,
            hide_index=True
        )

# ----------------------------------------------------
# TAB 2: 主力資金異動
# ----------------------------------------------------
with tab2:
    st.markdown("#### 🌊 美股主力資金異動與暗盤偷步雷達")
    st.dataframe(
        df_results[['Symbol', 'Price', 'Change', 'Flow_Status', 'CMF', 'Pocket_Pivot', 'RVOL', 'RS', 'Score', 'Setup_Type']],
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------------------------
# TAB 3: 核心自選情報
# ----------------------------------------------------
with tab3:
    st.markdown("#### 🛡️ 核心持倉實戰情報 (TSLA · AAOI · NVDA · MU · BE · NBIS · DDOG)")
    df_core = df_results[df_results['Symbol'].isin(CORE_PORTFOLIO_SYMBOLS)].copy()
    st.dataframe(
        df_core[['Symbol', 'Rank', 'Price', 'Change', 'RS', 'Score', 'Flow_Status', 'Setup_Type', 'Entry', 'Entry_Diff', 'Stop', 'Stop_Pct', 'Target_2R', 'Target_3R']],
        use_container_width=True,
        hide_index=True
    )

# ----------------------------------------------------
# TAB 4: TradingView 專業畫圖 (帶 7 維檢核)
# ----------------------------------------------------
with tab4:
    selected_stock = st.selectbox("選擇要分析的標的：", df_results['Symbol'].tolist(), index=0)
    stock_row = df_results[df_results['Symbol'] == selected_stock].iloc[0]

    c_r1, c_r2 = st.columns([1.1, 1.9])
    with c_r1:
        st.markdown(f"##### 📋 **{selected_stock}** J Law 7 維檢核")
        checklist = [
            ("1. Stage 2 趨勢範式", stock_row['Stage2'] == "符合", "股價 > 50SMA > 150SMA > 200SMA。"),
            ("2. RS 領頭羊地位 (≥80)", stock_row['RS'] >= 80, f"當前 RS 為 {stock_row['RS']} 分。"),
            ("3. VCP 波動收窄蓄勢", any("VCP" in r for r in stock_row['Reasons']), "ATR 收斂，主力鎖倉。"),
            ("4. 主力資金與口袋買點", stock_row['CMF'] > 0.05 or stock_row['Pocket_Pivot'] == "🔥 觸發", f"CMF: {stock_row['CMF']}，狀態: {stock_row['Flow_Status']}。"),
            ("5. 20 EMA 動態支撐", abs(stock_row['Dist_20EMA']) <= 3.0, f"距 20 EMA 僅 {stock_row['Dist_20EMA']}%。"),
            ("6. 量能蓄勢與突破", stock_row['RVOL'] >= 1.2 or stock_row['RVOL'] < 0.8, f"量比 (RVOL) 為 {stock_row['RVOL']}x。"),
            ("7. 結構點位設定", True, f"規劃買點 ${stock_row['Entry']:.2f}。")
        ]
        for title, passed, desc in checklist:
            s_icon = "✅" if passed else "⚠️"
            b_color = "#10B981" if passed else "#F59E0B"
            st.markdown(f"""
            <div style="background:rgba(13,18,27,0.8); border-left:3px solid {b_color}; padding:8px 12px; margin-bottom:6px; border-radius:4px; border:1px solid rgba(255,255,255,0.05); border-left-width:3px;">
                <div style="font-weight:700; color:#FFF; font-size:12px;">{s_icon} {title}</div>
                <div style="font-size:11px; color:#94A3B8;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with c_r2:
        tv_code = f"""
        <div class="tradingview-widget-container" style="height:480px;width:100%;">
          <div id="tv_{selected_stock}" style="height:calc(100% - 32px);width:100%;"></div>
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
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tv_{selected_stock}"
          }});
          </script>
        </div>
        """
        components.html(tv_code, height=490)

# ----------------------------------------------------
# TAB 5: 1% 風險下單與金字塔加倉
# ----------------------------------------------------
with tab5:
    target_calc_sym = st.selectbox("選擇計算下單標的：", df_results['Symbol'].tolist(), index=0, key="calc_box")
    stock_row = df_results[df_results['Symbol'] == target_calc_sym].iloc[0]

    inp_c1, inp_c2 = st.columns(2)
    with inp_c1:
        account_capital = st.number_input("賬戶總資產 ($)", value=50000, step=5000)
    with inp_c2:
        risk_pct = st.slider("單筆最大承受風險 (%)", 0.5, 2.5, 1.0, 0.1)

    max_risk_dollars = account_capital * (risk_pct / 100.0)
    target_entry = stock_row['Entry']
    target_stop = stock_row['Stop']
    target_risk_per_share = stock_row['Risk_Per_Share']
    calc_shares = int(max_risk_dollars / target_risk_per_share) if target_risk_per_share > 0 else 0

    st.markdown(f"""
    <div style="background:rgba(13,18,27,0.85); backdrop-filter:blur(16px); border:1px solid rgba(255,255,255,0.08); border-left:4px solid #10B981; padding:16px; border-radius:8px; font-family:'JetBrains Mono'; font-size:13px; line-height:2.0; margin-top:10px;">
        <div style="font-weight:800; color:#FFF; font-size:15px; margin-bottom:6px;">🛡️ OPTIMUS 1% 風控執行指令</div>
        • 推薦買入股數: <b style="color:#10B981; font-size:20px;">{calc_shares} 股</b><br>
        • 樞紐買點 (Limit): <b>${target_entry:.2f}</b> │ 條件止損 (Stop): <b style="color:#F87171;">${target_stop:.2f} ({stock_row['Stop_Pct']}%)</b><br>
        • 趁強賣出 (2R 平半): <b style="color:#38BDF8;">${stock_row['Target_2R']:.2f}</b> (平 {calc_shares // 2} 股) │ 趁弱移停 (3R): <b style="color:#FBBF24;">${stock_row['Target_3R']:.2f}</b>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("##### ⚡ J Law 冠軍右側金字塔加倉計劃")
    base_shares = int(calc_shares * 0.5)
    add1_shares = int(calc_shares * 0.3)
    add2_shares = int(calc_shares * 0.2)
    p1, p2, p3 = st.columns(3)
    p1.info(f"第 1 注 (50% 底倉): {base_shares} 股 @ ${target_entry:.2f}")
    p2.warning(f"第 2 注 (30% 次注): {add1_shares} 股 @ ~${round(target_entry*1.04, 2)} (浮盈加碼，止損移至保本)")
    p3.success(f"第 3 注 (20% 主升): {add2_shares} 股 @ ~${round(target_entry*1.08, 2)} (沿 20 EMA 移動止損)")
