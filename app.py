import streamlit as st
import streamlit.components.v1 as components

def inject_tesla_cyber_ui():
    """
    Tesla Cybercab & Cybertruck In-Car OS 12.0 系統級 UI 引擎
    深度重構所有原生組件，打造高對比、超窄邊框、無噪點 OLED 視覺
    """
    cyber_bg = "https://images.unsplash.com/photo-1544829099-b9a0c07fad1a?auto=format&fit=crop&w=2600&q=80"
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,300;0,400;0,600;0,700;0,800;1,700&family=Space+Grotesk:wght@400;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* 1. 頁面全局視角與背景架構 */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 98.5% !important;
        }}

        .stApp {{
            background: 
                radial-gradient(circle at 50% 0%, rgba(232, 33, 39, 0.14) 0%, transparent 45%),
                linear-gradient(180deg, rgba(6, 8, 14, 0.94) 0%, rgba(9, 12, 19, 0.98) 100%),
                url('{cyber_bg}') no-repeat center center fixed !important;
            background-size: cover !important;
            color: #E2E8F0;
            font-family: 'Inter', -apple-system, sans-serif;
            letter-spacing: -0.01em;
        }}

        /* 2. Tesla 側邊欄：消光槍灰色鈦金屬風格 */
        section[data-testid="stSidebar"] {{
            background: rgba(8, 11, 18, 0.96) !important;
            backdrop-filter: blur(30px) saturate(180%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 10px 0 30px rgba(0, 0, 0, 0.8);
        }}
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 1.8rem !important;
        }}

        /* 3. 頂部車機狀態儀表 (Tesla Status Banner) */
        .tesla-cluster-banner {{
            background: linear-gradient(90deg, rgba(14, 19, 30, 0.92) 0%, rgba(19, 25, 38, 0.85) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top: 3px solid #E82127;
            border-radius: 10px;
            padding: 14px 24px;
            margin-bottom: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            backdrop-filter: blur(20px);
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7);
        }}

        /* 4. Tesla PRND 檔位控制盒 */
        .tesla-gear-box {{
            display: inline-flex;
            background: rgba(4, 6, 11, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 900;
            font-size: 13px;
        }}
        .gear-item {{
            padding: 5px 12px;
            border-radius: 5px;
            color: #475569;
            transition: all 0.2s ease;
        }}
        .gear-active-drive {{
            background: #10B981 !important;
            color: #05070A !important;
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.8);
        }}
        .gear-active-neutral {{
            background: #F59E0B !important;
            color: #05070A !important;
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.8);
        }}
        .gear-active-park {{
            background: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 18px rgba(232, 33, 39, 0.85);
        }}

        /* 5. 導航欄：Tesla 懸浮中控觸控 Bar (Segmented Control) */
        div[role="radiogroup"] {{
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 8px !important;
            background: rgba(11, 15, 25, 0.85) !important;
            padding: 6px 8px !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            margin-bottom: 18px !important;
            backdrop-filter: blur(16px);
        }}
        div[role="radiogroup"] > label {{
            background: rgba(18, 24, 38, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 6px !important;
            padding: 8px 18px !important;
            color: #94A3B8 !important;
            cursor: pointer !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12px !important;
            font-weight: 700 !important;
        }}
        div[role="radiogroup"] > label:hover {{
            border-color: rgba(232, 33, 39, 0.6) !important;
            color: #FFFFFF !important;
            transform: translateY(-1px);
        }}
        div[role="radiogroup"] input[type="radio"] {{
            display: none !important;
        }}
        div[role="radiogroup"] > label:has(input:checked) {{
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.35) 0%, rgba(18, 24, 38, 0.98) 100%) !important;
            border-color: #E82127 !important;
            color: #FFFFFF !important;
            box-shadow: 0 0 16px rgba(232, 33, 39, 0.45) !important;
        }}

        /* 6. Cybertruck 幾何切角資訊卡 (OLED Glass Cards) */
        .cyber-card {{
            background: rgba(13, 17, 28, 0.85);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 16px 18px;
            margin-bottom: 12px;
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            min-height: 215px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}
        .cyber-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: transparent;
            transition: all 0.2s ease;
        }}
        .cyber-card:hover {{
            border-color: #E82127;
            box-shadow: 0 14px 35px rgba(232, 33, 39, 0.25);
            transform: translateY(-3px);
        }}
        .cyber-card:hover::before {{
            background: #E82127;
        }}

        /* 7. 徽章系統：絕對單行防斷裂 */
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
            text-transform: uppercase;
        }}
        .badge-diamond {{ background: rgba(6, 182, 212, 0.2); color: #22D3EE; border: 1px solid #06B6D4; }}
        .badge-gold {{ background: rgba(234, 179, 8, 0.2); color: #FACC15; border: 1px solid #EAB308; }}
        .badge-green {{ background: rgba(16, 185, 129, 0.2); color: #34D399; border: 1px solid #10B981; }}
        .badge-red {{ background: rgba(239, 68, 68, 0.2); color: #F87171; border: 1px solid #EF4444; }}
        .badge-tesla {{ background: rgba(232, 33, 39, 0.25); color: #FF6B6B; border: 1px solid #E82127; }}
        .badge-flow {{ background: rgba(168, 85, 247, 0.2); color: #C084FC; border: 1px solid #A855F7; }}

        /* 8. Tesla 車載 HUD 數據磚 */
        .hud-telemetry {{
            background: rgba(11, 15, 24, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-left: 3px solid #E82127;
            border-radius: 6px;
            padding: 12px 16px;
            backdrop-filter: blur(16px);
        }}
        .hud-title {{
            font-size: 10.5px;
            color: #94A3B8;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 1px;
            text-transform: uppercase;
        }}
        .hud-val {{
            font-size: 25px;
            font-weight: 900;
            color: #FFFFFF;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 4px;
        }}

        /* 9. 模組抬頭與操作盒 */
        .section-header {{
            background: rgba(13, 17, 28, 0.9);
            border-left: 4px solid #E82127;
            padding: 12px 18px;
            border-radius: 6px;
            margin-bottom: 14px;
            backdrop-filter: blur(12px);
        }}
        .action-box {{
            background: rgba(8, 12, 20, 0.95);
            border: 1px solid rgba(232, 33, 39, 0.35);
            border-radius: 8px;
            padding: 18px;
            font-family: 'JetBrains Mono', monospace;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6);
        }}

        /* 10. 全面重構 Streamlit 原生表單控件 (Input, Select, Slider) */
        div[data-baseweb="select"] > div {{
            background-color: rgba(14, 19, 31, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 6px !important;
            color: #FFF !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        div[data-baseweb="select"] > div:hover {{
            border-color: #E82127 !important;
        }}
        div[data-baseweb="input"] > div {{
            background-color: rgba(14, 19, 31, 0.9) !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            border-radius: 6px !important;
            color: #FFF !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}
        div[data-baseweb="input"] > div:focus-within {{
            border-color: #E82127 !important;
            box-shadow: 0 0 12px rgba(232, 33, 39, 0.5) !important;
        }}
        /* 自定義按鈕為 Tesla 賽車紅科技切角按鈕 */
        div.stButton > button:first-child {{
            background: linear-gradient(135deg, #1E2536 0%, #0E131F 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid #E82127 !important;
            border-radius: 6px !important;
            padding: 10px 22px !important;
            font-family: 'JetBrains Mono', monospace !important;
            font-weight: 800 !important;
            letter-spacing: 1px !important;
            box-shadow: 0 4px 14px rgba(232, 33, 39, 0.25) !important;
            transition: all 0.25s ease !important;
        }}
        div.stButton > button:first-child:hover {{
            background: #E82127 !important;
            color: #FFF !important;
            box-shadow: 0 0 22px rgba(232, 33, 39, 0.7) !important;
            transform: translateY(-2px);
        }}

        /* 呼吸警報光暈 */
        @keyframes pulse-tesla {{
            0% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0.6); }}
            70% {{ box-shadow: 0 0 0 10px rgba(232, 33, 39, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(232, 33, 39, 0); }}
        }}
        .alert-tesla {{
            background: linear-gradient(135deg, rgba(232, 33, 39, 0.25) 0%, rgba(14, 19, 31, 0.95) 100%);
            border: 1px solid #E82127;
            border-radius: 8px;
            padding: 12px 18px;
            margin-bottom: 14px;
            animation: pulse-tesla 2.2s infinite;
        }}

        /* 自定義極細滾動條 */
        ::-webkit-scrollbar {{
            width: 6px;
            height: 6px;
        }}
        ::-webkit-scrollbar-track {{
            background: rgba(5, 7, 12, 0.8);
        }}
        ::-webkit-scrollbar-thumb {{
            background: rgba(255, 255, 255, 0.15);
            border-radius: 3px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #E82127;
        }}
    </style>
    """, unsafe_allow_html=True)
