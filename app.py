import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests 
import streamlit.components.v1 as components

# ==========================================
# 1. 系統視覺核心 (Cyber-Chinese UI)
# ==========================================
st.set_page_config(page_title="J Law Alpha Station", layout="wide", page_icon="🦅")

# 背景：Dark Abstract Data Nodes (暗黑數據節點 - 型格風)
BG_URL = "https://images.unsplash.com/photo-1639322537228-f710d846310a?q=80&w=2070&auto=format&fit=crop"

# 定義 CSS (純文字模式，安全注入)
main_css = """
<style>
    /* 引入 Google 中文黑體 + 數字等寬字體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;700&family=JetBrains+Mono:wght@400;700&display=swap');

    /* --- 全局背景 (型格暗黑) --- */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.95)), url("REPLACE_BG_URL");
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
        color: #E0E0E0;
        font-family: 'Noto Sans TC', sans-serif; /* 全局中文優化 */
    }
    
    /* 側邊欄：磨砂黑 */
    section[data-testid="stSidebar"] {
        background: rgba(10, 10, 10, 0.95);
        border-right: 1px solid #333;
        backdrop-filter: blur(20px);
    }
    
    /* --- 股票列表：極簡數據磚 --- */
    div[role="radiogroup"] > label > div:first-child { display: none !important; }
    
    div[role="radiogroup"] { gap: 4px; }
    
    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.03);
        border: 1px solid #333;
        padding: 12px 15px;
        border-radius: 4px;
        transition: all 0.2s ease;
        font-family: 'JetBrains Mono', monospace;
        font-size: 14px;
        color: #aaa;
        cursor: pointer;
    }
    
    div[role="radiogroup"] > label:hover {
        border-color: #00E676;
        color: #fff;
        background: rgba(0, 230, 118, 0.05);
        transform: translateX(3px);
    }
    
    /* 選中狀態：發光綠條 */
    div[role="radiogroup"] > label[data-checked="true"] {
        background: #000 !important;
        border: 1px solid #00E676;
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.15);
        color: #00E676 !important;
        font-weight: 700;
    }

    /* --- 數據儀表板 --- */
    .stat-card {
        background: #111;
        border: 1px solid #333;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
    }
    .stat-label { font-size: 12px; color: #666; letter-spacing: 1px; }
    .stat-value { font-size: 24px; font-weight: 700; color: #fff; margin-top: 5px; font-family: 'JetBrains Mono'; }

    /* --- J Law 戰術報告面板 --- */
    .repo
