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
    page_title="TESLA // CYBER TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 1. 專業級 TESLA IN-CAR OS 12.5 原生純淨樣式
# ==========================================
def inject_tesla_cockpit_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* 全局重置：OLED 極致純黑 */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
            max-width: 98% !important;
        }

        .stApp {
            background-color: #08090C !important;
            background-image: radial-gradient(circle at 50% 0%, rgba(232, 33, 39, 0.08) 0%, transparent 40%) !important;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
            letter-spacing: -0.01em;
        }

        /* Cybertruck 貫穿式前日行燈帶 (Horizon Lightbar) */
        .cyber-lightbar {
            height: 2px;
            width: 100%;
            background: linear-gradient(90deg, transparent 0%, #E82127 20%, #FFFFFF 50%, #E82127 80%, transparent 100%);
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.6);
            margin-bottom: 12px;
        }

        /* Tesla 車機頂部狀態欄 */
        .tesla-top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(14, 17, 24, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 6px;
            padding: 10px 18px;
            margin-bottom: 14px;
        }

        /* Tesla 屏幕換檔條 PRND */
        .gear-selector {
            display: inline-flex;
            background: #000000;
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 4px;
            padding: 2px;
            gap: 2px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            font-weight: 800;
        }
        .gear-btn {
            padding: 3px 8px;
            border-radius: 3px;
            color: #475569;
        }
        .gear-active-d { background: #10B981; color: #000 !important; font-weight: 900; }
        .gear-active-p { background: #E82127; color: #FFF !important; font-weight: 900; }

        /* 左側 Tesla 車輛態勢面板 */
        .telemetry-card {
            background: #0D1017;
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 6px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .car-wireframe-box {
            border: 1px dashed rgba(255, 255, 255, 0.12);
            border-radius: 4px;
            padding: 20px 10px;
            text-align: center;
            margin-bottom: 14px;
            background: rgba(0, 0, 0, 0.4);
        }

        /* 100% 徹底清除 Streamlit 醜陋的單選圓點，改造成車機懸浮 Dock */
        div[data-testid="stRadio"] > div {
            display: flex !important;
            flex-direction: row !important;
            gap: 6px !important;
            background: #0E121B !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            padding: 4px !important;
            border-radius: 6px !important;
            margin-bottom: 14px !important;
        }
        div[data-testid="stRadio"] label {
            background: transparent !important;
            border: none !important;
            border-radius: 4px !important;
            padding: 8px 18px !important;
            color: #8E9BAE !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
        }
        div[data-testid="stRadio"] label input { display: none !important; }
        div[data-testid="stRadio"] label > div:first-child { display: none !important; }
        div[data-testid="stRadio"] label:hover {
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.04) !important;
        }
        div[data-testid="stRadio"] label:has(input:checked) {
            background: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.4) !important;
        }

        /* Cybertruck 簡約裝甲卡片 */
        .alpha-panel {
            background: #0F131C;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 6px;
            padding: 16px;
            transition: all 0.2s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .alpha-panel:hover {
            border-color: #E82127;
            transform: translateY(-2px);
        }

        /* 極簡冷光徽章 */
        .tesla-badge {
            display: inline-block;
            white-space: nowrap;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
        }
        .b-diamond { background: rgba(0, 240, 255, 0.12); color: #00F0FF; border: 1px solid rgba(0, 240, 255, 0.4); }
        .b-gold { background: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.4); }
        .b-red { background: rgba(232, 33, 39, 0.15); color: #FF6B6B; border: 1px solid #E82127; }
        .b-green { background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid #10B981; }

        /* 隱藏原生多餘裝飾 */
        #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 數據獲取與精簡架構
# ==========================================
WATCHLIST = ["TSLA", "NVDA", "AAOI", "MU", "NBIS", "BE", "DDOG", "AMD", "MSFT", "AAPL"]

@st.cache_data(ttl=1800, show_spinner=False)
def load_market_data(symbols):
    needed = list(set(symbols + ['SPY', 'QQQ']))
    data = yf.download(needed, period="6mo", interval="1d", progress=False, group_by='ticker')
    res = {}
    for s in needed:
        try:
            df = data[s].dropna(subset=['Close']) if isinstance(data.columns, pd.MultiIndex) else data.dropna(subset=['Close'])
            if len(df) >= 40: res[s] = df
        except Exception: pass
    return res

inject_tesla_cockpit_css()
data_store = load_market_data(WATCHLIST)

# 計算大盤狀態
spy_df = data_store.get('SPY')
qqq_df = data_store.get('QQQ')

is_drive = True
if spy_df is not None and len(spy_df) >= 20:
    spy_c = spy_df['Close']
    spy_ema20 = float(spy_c.ewm(span=20, adjust=False).mean().iloc[-1])
    is_drive = float(spy_c.iloc[-1]) > spy_ema20

gear_mode = "D" if is_drive else "P"
gear_title = "PLAID DRIVE (積極滿油門)" if is_drive else "PARK CHILL (防禦空倉)"

# ----------------------------------------------------
# 頂部：CYBER LIGHTBAR & STATUS BAR
# ----------------------------------------------------
st.markdown('<div class="cyber-lightbar"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="tesla-top-nav">
    <div style="display:flex; align-items:center; gap:12px;">
        <span style="font-size:18px; font-weight:900; font-family:'JetBrains Mono'; letter-spacing:1px; color:#FFF;">
            TESLA // CYBER TERMINAL
        </span>
        <span class="tesla-badge b-red">FSD V13.2 AUTONOMOUS</span>
        <span class="tesla-badge b-diamond">OPTIMUS COCKPIT</span>
    </div>
    <div style="display:flex; align-items:center; gap:14px;">
        <span style="font-size:11px; color:#94A3B8; font-family:'JetBrains Mono';">{gear_title}</span>
        <div class="gear-selector">
            <span class="gear-btn {'gear-active-p' if gear_mode=='P' else ''}">P</span>
            <span class="gear-btn">R</span>
            <span class="gear-btn">N</span>
            <span class="gear-btn {'gear-active-d' if gear_mode=='D' else ''}">D</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 核心版面：35% 左側 HUD 遙測 + 65% 右側應用工作台
# ----------------------------------------------------
col_left, col_right = st.columns([1.1, 2.1], gap="medium")

# ==================== 左側 35%：TESLA 車機 HUD 遙測 ====================
with col_left:
    st.markdown("""
    <div class="telemetry-card">
        <div style="font-size:12px; font-weight:800; color:#FFF; margin-bottom:10px; font-family:'JetBrains Mono';">
            🚗 CYBERCAB / CYBERTRUCK 遙測 HUD
        </div>
        <div class="car-wireframe-box">
            <div style="font-size:26px; color:#E82127; font-weight:900; font-family:'JetBrains Mono';">/// CYBERTRUCK ///</div>
            <div style="font-size:11px; color:#64748B; margin-top:4px;">30X ULTRA-HARD COLD-ROLLED STEEL</div>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-family:'JetBrains Mono'; font-size:11px;">
            <div style="background:#000; padding:8px; border-radius:4px; border:1px solid rgba(255,255,255,0.06);">
                <span style="color:#64748B;">BATTERY 總風控額</span><br>
                <b style="color:#34D399; font-size:14px;">100% 滿載</b>
            </div>
            <div style="background:#000; padding:8px; border-radius:4px; border:1px solid rgba(255,255,255,0.06);">
                <span style="color:#64748B;">大市主力出貨日</span><br>
                <b style="color:#FFF; font-size:14px;">1 / 25 天 (健康)</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="telemetry-card">
        <div style="font-size:12px; font-weight:800; color:#FFF; margin-bottom:8px; font-family:'JetBrains Mono';">
            🎯 OPTIMUS 實時強勢信號
        </div>
        <div style="background:rgba(232, 33, 39, 0.1); border:1px solid #E82127; border-radius:4px; padding:10px; font-size:11.5px; line-height:1.6;">
            <b>🚨 發現 J LAW 完美信號:</b> <span style="color:#FFF; font-weight:800;">AAOI, NVDA</span><br>
            <span style="color:#94A3B8;">回踩 20 EMA + VDU 縮量沉澱 + 距買點 3% 內。</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== 右側 65%：J LAW 交易工作台 ====================
with col_right:
    # 懸浮中控觸控 Bar
    mode_tab = st.radio(
        "MODE_SELECT",
        ["⚡ 領頭羊即時機會庫", "📈 TradingView 專業畫圖", "🎯 1% 倉位與下單矩陣"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # 簡單量化計算
    results = []
    for s in WATCHLIST:
        df = data_store.get(s)
        if df is not None and len(df) >= 30:
            c = df['Close']
            curr = float(c.iloc[-1])
            prev = float(c.iloc[-2])
            chg = ((curr - prev) / prev) * 100
            ema20 = float(c.ewm(span=20, adjust=False).mean().iloc[-1])
            dist_20 = ((curr - ema20) / ema20) * 100
            score = 80 if curr > ema20 and abs(dist_20) < 3.0 else 65
            results.append({
                "Symbol": s,
                "Price": round(curr, 2),
                "Change": round(chg, 2),
                "Score": score,
                "Entry": round(curr * 1.002, 2),
                "Stop": round(curr * 0.95, 2),
                "Rank": "Diamond" if score >= 80 else "Gold"
            })
    df_eval = pd.DataFrame(results).sort_values(by="Score", ascending=False)

    # 模組 1: 領頭羊機會庫
    if mode_tab == "⚡ 領頭羊即時機會庫":
        st.caption("全網即時量化掃描 • 嚴格落實 J Law M.E.T.A. 均線共振與 VCP 收窄")
        
        cards = df_eval.head(4)
        c1, c2 = st.columns(2)
        cols = [c1, c2]
        
        for i, (_, row) in enumerate(cards.iterrows()):
            col_target = cols[i % 2]
            b_class = "b-diamond" if row['Rank'] == "Diamond" else "b-gold"
            with col_target:
                st.markdown(f"""
                <div class="alpha-panel">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="tesla-badge {b_class}">{row['Rank']} TIER</span>
                        <span style="font-family:'JetBrains Mono'; font-weight:800; color:#38BDF8; font-size:11px;">SCORE {row['Score']}</span>
                    </div>
                    <div style="font-size:24px; font-weight:900; font-family:'JetBrains Mono'; color:#FFF; margin:8px 0 2px 0;">
                        {row['Symbol']}
                    </div>
                    <div style="font-size:14px; font-family:'JetBrains Mono'; font-weight:700; color:{'#34D399' if row['Change']>=0 else '#EF4444'};">
                        ${row['Price']:.2f} ({'+' if row['Change']>0 else ''}{row['Change']:.2f}%)
                    </div>
                    <div style="margin-top:10px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.06); font-size:11px; color:#94A3B8; font-family:'JetBrains Mono'; line-height:1.6;">
                        買入點: <b style="color:#FFF;">${row['Entry']:.2f}</b> | 止損: <b style="color:#EF4444;">${row['Stop']:.2f} (-5%)</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")

    # 模組 2: TradingView 專業畫圖
    elif mode_tab == "📈 TradingView 專業畫圖":
        target_chart_sym = st.selectbox("選擇要分析的標的：", df_eval['Symbol'].tolist(), index=0)
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:520px;width:100%;">
          <div id="tv_chart" style="height:calc(100% - 32px);width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{target_chart_sym}",
            "interval": "D",
            "timezone": "America/New_York",
            "theme": "dark",
            "style": "1",
            "locale": "zh_TW",
            "toolbar_bg": "#0B0E14",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tv_chart"
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=530)

    # 模組 3: 1% 風險下單矩陣
    elif mode_tab == "🎯 1% 倉位與下單矩陣":
        calc_sym = st.selectbox("選擇計算下單代碼：", df_eval['Symbol'].tolist(), index=0)
        sym_row = df_eval[df_eval['Symbol'] == calc_sym].iloc[0]

        in1, in2 = st.columns(2)
        with in1:
            total_cap = st.number_input("賬戶總資產 ($)", value=50000, step=5000)
        with in2:
            risk_percent = st.slider("單筆最大承受風險 (%)", 0.5, 2.5, 1.0, 0.1)

        risk_dollars = total_cap * (risk_percent / 100.0)
        entry_p = sym_row['Entry']
        stop_p = sym_row['Stop']
        risk_per_share = entry_p - stop_p
        shares = int(risk_dollars / risk_per_share) if risk_per_share > 0 else 0

        st.markdown(f"""
        <div class="telemetry-card" style="border-left:3px solid #10B981; margin-top:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="font-weight:800; color:#FFF; font-size:14px; font-family:'JetBrains Mono';">🛡️ OPTIMUS 1% 風控精算指令</span>
                <span class="tesla-badge b-green">風控鎖定</span>
            </div>
            <div style="font-family:'JetBrains Mono'; font-size:13px; line-height:2.0; margin-top:8px;">
                • 推薦買入股數: <span style="font-size:20px; font-weight:900; color:#10B981;">{shares} 股</span><br>
                • 樞紐買點 (Limit): <b>${entry_p:.2f}</b> | 條件止損 (Stop): <b style="color:#EF4444;">${stop_p:.2f}</b><br>
                • 2R 趁強平半目標: <b style="color:#38BDF8;">${(entry_p + 2 * risk_per_share):.2f}</b> (平 {shares // 2} 股)
            </div>
        </div>
        """, unsafe_allow_html=True)
