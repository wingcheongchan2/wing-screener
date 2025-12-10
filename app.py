import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統視覺核心 (CSS Architecture)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 背景：專業金融藍 (Professional FinTech Blue)
BG_URL = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop"

st.markdown(f"""
<style>
    /* 引入專業等寬字體 (Terminal Style) */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;800&display=swap');

    /* --- 全局背景重構 --- */
    .stApp {{
        background-image: linear-gradient(rgba(10, 25, 47, 0.85), rgba(10, 25, 47, 0.95)), url("{BG_URL}");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #e6f1ff;
        font-family: 'Inter', sans-serif;
    }}
    
    /* 側邊欄：玻璃擬態深藍 */
    section[data-testid="stSidebar"] {{
        background: rgba(17, 34, 64, 0.95);
        border-right: 1px solid #233554;
        backdrop-filter: blur(10px);
    }}
    
    /* --- 股票列表：高密度數據磁貼 (Critical Fix) --- */
    /* 隱藏原生 Radio 圓圈 */
    div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}
    
    div[role="radiogroup"] {{
        gap: 0px; /* 消除間隙 */
    }}
    
    div[role="radiogroup"] > label {{
        background: transparent;
        border-bottom: 1px solid #233554;
        padding: 12px 15px;
        margin: 0;
        border-radius: 0;
        transition: all 0.2s ease;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #8892b0;
    }}
    
    /* 滑鼠懸停 */
    div[role="radiogroup"] > label:hover {{
        background: rgba(100, 255, 218, 0.05);
        color: #64ffda;
        padding-left: 20px; /* 動態位移感 */
    }}
    
    /* 選中狀態 (專業霓虹綠) */
    div[role="radiogroup"] > label[data-checked="true"] {{
        background: rgba(17, 34, 64, 1) !important;
        border-left: 4px solid #64ffda; /* 左側亮條 */
        color: #e6f1ff !important;
        font-weight: 700;
        padding-left: 20px;
    }}

    /* --- 數據儀表板 (Dashboard) --- */
    .metric-container {{
        display: flex;
        gap: 15px;
        margin-bottom: 20px;
    }}
    .stat-card {{
        flex: 1;
        background: #112240;
        border: 1px solid #233554;
        padding: 15px;
        border-radius: 4px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    .stat-label {{ font-size: 11px; color: #64ffda; letter-spacing: 1px; text-transform: uppercase; font-family: 'JetBrains Mono'; }}
    .stat-value {{ font-size: 24px; font-weight: 700; color: #fff; margin-top: 5px; }}

    /* --- J Law 專業報告面板 --- */
    .report-panel {{
        background: #0a192f;
        border: 1px solid #233554;
        border-top: 3px solid #64ffda; /* 頂部亮條 */
        padding: 25px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.8;
        color: #a8b2d1;
        font-size: 14px;
        margin-bottom: 20px;
    }}
    .report-highlight {{ color: #64ffda; font-weight: bold; }}
    .report-section {{ border-bottom: 1px solid #233554; padding-bottom: 10px; margin-bottom: 10px; }}
    
    /* 按鈕樣式 */
    div.stButton > button {{
        background: transparent;
        border: 1px solid #64ffda;
