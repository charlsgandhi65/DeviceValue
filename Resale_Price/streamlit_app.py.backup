"""
streamlit_app.py
----------------
Used Phone Price Predictor – Premium Edition (Platinum UI).

Run with:
    streamlit run streamlit_app.py
"""

import sys
import os
import pandas as pd
import streamlit as st
import subprocess
import random
import base64
import plotly.graph_objects as go
import requests
import urllib.parse  # Ensure this is here
import re
from dotenv import load_dotenv
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

# Make sure src/ is importable from anywhere
sys.path.insert(0, os.path.dirname(__file__))

from predict import (
    load_artifacts,
    predict_price,
    get_known_brands,
    get_known_conditions,
    get_known_models,
)

# ── Load environment variables from .env ────────────────────────────────────────
load_dotenv()

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Phone Resale Pro", page_icon="📱", layout="wide")

# ── Custom Premium CSS ────────────────────────────────────────────────────────
try:
    with open(
        os.path.join(os.path.dirname(__file__), "assets", "minimal_nebula.png"), "rb"
    ) as f:
        nebula_b64 = base64.b64encode(f.read()).decode()
    with open(
        os.path.join(os.path.dirname(__file__), "assets", "flagship_transparent.png"),
        "rb",
    ) as f:
        samsung_b64 = base64.b64encode(f.read()).decode()
    with open(
        os.path.join(os.path.dirname(__file__), "assets", "iphone_wa_transparent.png"),
        "rb",
    ) as f:
        iphone_b64 = base64.b64encode(f.read()).decode()
except Exception:
    nebula_b64 = ""
    samsung_b64 = ""
    iphone_b64 = ""

st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Space+Grotesk:wght@700&display=swap');

    :root {{
        --text-color: #E2E8F0;
        --accent-glow: rgba(94, 114, 228, 0.3);
        --glass-bg: rgba(10, 15, 25, 0.4);
    }}

    .stApp {{
        background: radial-gradient(circle at 50% 0%, #0c0e14 0%, #02040a 100%);
        color: var(--text-color);
        font-family: 'Outfit', sans-serif;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(15px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .fade-in {{ animation: fadeIn 1.2s ease-out forwards; }}



    /* Hide Streamlit Branding and Platform UI */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    [data-testid="stHeader"] {{display: none;}}
    [data-testid="stToolbar"] {{display: none;}}
    [data-testid="stDecoration"] {{display: none;}}
    [data-testid="stStatusWidget"] {{display: none;}}
    


    [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"] {{
        background: rgba(10, 15, 25, 0.6) !important;
        padding: 3rem !important;
        border-radius: 32px !important;
        border: 1px solid rgba(139, 92, 246, 0.25) !important;
        backdrop-filter: blur(40px) !important;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(139, 92, 246, 0.05) !important;
        margin-bottom: 0.5rem !important;
        transition: transform 0.3s ease, border-color 0.3s ease !important;
    }}

    [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:hover {{
        transform: translateY(-5px);
        border-color: rgba(139, 92, 246, 0.5) !important;
    }}

    /* Premium Input Styling */
    div[data-testid="stSelectbox"] > div {{
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), rgba(15, 23, 42, 0.96) 35%, rgba(15, 23, 42, 0.98)) !important;
        border: 1px solid rgba(51, 65, 85, 0.95) !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        height: 52px !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important,
            inset 0 -1px 2px rgba(0, 0, 0, 0.18) !important,
            0 10px 30px rgba(15, 23, 42, 0.25) !important;
        backdrop-filter: blur(8px) !important;
    }}

    div[data-testid="stSelectbox"] > div:focus-within {{
        border-color: #8b5cf6 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important,
            inset 0 -1px 2px rgba(0, 0, 0, 0.24) !important,
            0 0 0 3px rgba(139, 92, 246, 0.2) !important;
    }}

    [data-testid="stPopover"] > div {{
        background-color: rgba(15, 23, 42, 0.95) !important;
        border: 1px solid rgba(51, 65, 85, 0.95) !important;
        border-radius: 12px !important;
        box-shadow: 0 20px 45px rgba(15, 23, 42, 0.35) !important;
        backdrop-filter: blur(18px) !important;
        color: #e2e8f0 !important;
    }}

    [data-testid="stPopover"] button {{
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(15, 23, 42, 0.98) 38%, rgba(15, 23, 42, 0.96)) !important;
        border: 1px solid rgba(51, 65, 85, 0.95) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        min-height: 52px !important;
        padding: 0 1rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 400 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06) !important,
            inset 0 -1px 2px rgba(0, 0, 0, 0.2) !important,
            0 10px 30px rgba(15, 23, 42, 0.35) !important;
        transition: all 0.2s ease !important;
        backdrop-filter: blur(8px) !important;
    }}

    [data-testid="stPopover"] button:hover,
    [data-testid="stPopover"] button:focus {{
        border-color: #8b5cf6 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important,
            inset 0 -1px 2px rgba(0, 0, 0, 0.24) !important,
            0 0 0 3px rgba(139, 92, 246, 0.2) !important;
        outline: none !important;
        background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(15, 23, 42, 1) 42%, rgba(15, 23, 42, 0.98)) !important;
    }}

    [data-testid="stPopover"] button > div {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
    }}

    /* Slider Overhaul */
    div[data-testid="stSlider"] {{
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
    }}

    .stSlider > div {{
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px;
    }}

    /* Labels */
    label[data-testid="stWidgetLabel"] p {{
        font-family: 'Outfit', sans-serif !important;
        font-weight: 400 !important;
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.025em !important;
        margin-bottom: 0.5rem !important;
    }}

    .price-value {{
        font-size: 3.5rem;
        font-weight: 800;
        color: #5e72e4; /* Premium Blue */
        text-shadow: 0 0 30px rgba(94, 114, 228, 0.3);
    }}

    button[kind="primary"] {{
        background: linear-gradient(135deg, #8b5cf6, #6366f1) !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        box-shadow: 0 10px 20px -5px rgba(139, 92, 246, 0.4) !important;
        transition: all 0.3s ease !important;
        margin-top: -0.8rem !important; /* Pulling up to almost touching distance */
    }}

    button[kind="primary"]:hover {{
        transform: scale(1.02) !important;
        box-shadow: 0 15px 30px -5px rgba(139, 92, 246, 0.6) !important;
    }}
    
    .result-box {{
        background: rgba(10, 15, 25, 0.6) !important;
        padding: 2.5rem !important;
        border-radius: 32px !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        backdrop-filter: blur(40px) !important;
        box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.7), 0 0 25px rgba(139, 92, 246, 0.3) !important;
        margin-bottom: 2rem !important;
        max-width: 450px;
        margin-left: auto; /* Shifting to right */
        text-align: left;
        animation: fadeIn 0.8s ease-out forwards;
    }}

    .label-text {{
        color: #94a3b8;
        font-size: 0.9rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}

    .info-tag {{
        display: inline-block;
        padding: 0.4rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 100px;
        font-size: 0.85rem;
        color: #e2e8f0;
        margin-right: 0.5rem;
        margin-top: 0.8rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}

    .phone-visual-card {{
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        margin-bottom: 1.5rem;
        overflow: hidden;
        animation: fadeIn 1s ease-out forwards;
    }}

    .footer {{
        text-align: center;
        padding: 2rem;
        opacity: 0.4;
        font-size: 0.8rem;
        letter-spacing: 0.05em;
    }}

    /* Extend Streamlit's mobile stacking behavior to Tablets perfectly */
    @media (max-width: 1024px) {{
        [data-testid="block-container"] {{
            max-width: 550px !important;
            margin: 0 auto !important;
        }}
        [data-testid="stHorizontalBlock"] {{
            flex-direction: column !important;
            gap: 1.5rem !important;
        }}
        [data-testid="column"], [data-testid="stColumn"] {{
            width: 100% !important;
            min-width: 100% !important;
            max-width: 100% !important;
            flex: none !important;
        }}
        .result-box {{
            margin: 0 auto 2rem auto !important;
        }}
    }}


    /* Responsive Hero Configuration */
    /* Responsive Hero Configuration */
    .hero-container {{
        width: 94%;
        margin: 1rem auto;
        position: relative;
        height: auto;
    }}
    .hero-glass-card {{
        position: relative;
        width: 100%;
        height: 175px;
        border-radius: 30px;
        border: 2px solid rgba(139,92,246,.78);
        backdrop-filter: blur(28px);
        box-shadow: 0 28px 70px rgba(0,0,0,.62), 0 0 28px rgba(139,92,246,.32);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 0 3rem;
        overflow: visible;
        transition: all .35s ease;
    }}
    .hero-glass-card:hover {{
        border-color: #a78bfa;
        box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.7), 0 0 35px rgba(139, 92, 246, 0.6);
    }}
    .hero-title {{
        font-family:'Space Grotesk',sans-serif;
        font-size: clamp(3rem,6vw,84px);
        line-height: .92;
        letter-spacing: -2px;
        margin: 0;
    }}
    .hero-subtitle {{
        font-size: 1.28rem;
        margin-top: 6px;
        max-width: 42rem;
        line-height: 1.35;
        color:#d7dce8;
    }}
    .samsung-overlay {{
        position:absolute;
        top:-42px;
        right:-18px;
        height:255px;
        z-index:102;
        filter:drop-shadow(0 28px 48px rgba(0,0,0,.65));
        transform:rotate(-7deg);
        animation: desktopFloatR 5.3s ease-in-out infinite !important;
        transform-origin: bottom center !important;
    }}
    .iphone-overlay {{
        position:absolute;
        top:18px;
        right:145px;
        height:168px;
        z-index:101;
        filter:drop-shadow(0 20px 38px rgba(0,0,0,.45));
        transform:rotate(-8deg);
        animation: desktopFloatL 4.2s ease-in-out infinite !important;
        transform-origin: bottom center !important;
    }}

    @keyframes desktopFloatL {{
        0%, 100% {{ transform: rotate(-8deg) translateY(0px); }}
        50%       {{ transform: rotate(-8deg) translateY(-14px); }}
    }}

    @keyframes desktopFloatR {{
        0%, 100% {{ transform: rotate(-7deg) translateY(0px); }}
        50%       {{ transform: rotate(-7deg) translateY(-10px); }}
    }}

    @media (min-width: 768px) {{
        .hero-container {{ width: 92%; margin-bottom: 2rem; height: 200px; }}
        .hero-glass-card {{ height: 158px; padding: 0 2.5rem; }}
        .hero-title {{ font-size: 4rem; }}
        .hero-subtitle {{ font-size: 1.25rem; margin-top: -2px; }}
        .samsung-overlay {{ top: -34px; right: -150px; height: 206px; }}
        .iphone-overlay {{ top: 19px; right: 180px; height: 139px; }}
    }}

    @media (min-width: 1024px) {{
        .hero-container {{ width: 100%; max-width: 1280px; margin-bottom: 3rem; height: 240px; }}
        .hero-glass-card {{ height: 270px; padding: 0 4rem; }}
        .hero-title {{ font-size: clamp(2.5rem, 6.5vw, 88px); }}
        .hero-subtitle {{ font-size: 1.5rem; margin-top: -4px; max-width: 36rem; }}
        .samsung-overlay {{ top: -45px; right: -80px; height: 375px; }}
        .iphone-overlay {{ top: 25px; right: 200px; height: 260px; }}
    }}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<style>
.drawer-btn {{
position: fixed;
top: 20px;
left: 20px;
z-index: 1000000;
background: rgba(15, 23, 42, 0.8);
border: 2px solid rgba(139, 92, 246, 0.5);
color: white;
width: 50px;
height: 50px;
border-radius: 50%;
display: flex;
align-items: center;
justify-content: center;
cursor: pointer;
transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
box-shadow: 0 0 15px rgba(139, 92, 246, 0.3);
}}
.drawer-btn:hover {{
transform: scale(1.1) rotate(90deg);
border-color: #8b5cf6;
box-shadow: 0 0 25px rgba(139, 92, 246, 0.6);
}}
.drawer-overlay {{
position: fixed;
inset: 0;
background: rgba(0, 0, 0, 0.5);
backdrop-filter: blur(4px);
z-index: 999998;
opacity: 0;
visibility: hidden;
transition: all 0.4s ease;
}}
    .drawer-panel {{
        position: fixed;
        top: 0;
        left: -400px;
        width: 380px;
        height: 100vh;
        background: rgba(6, 8, 12, 0.9);
        backdrop-filter: blur(40px);
        border-right: 1px solid rgba(139, 92, 246, 0.3);
        z-index: 999999;
        transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 60px 30px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }}
    .drawer-panel::-webkit-scrollbar {{
        width: 4px;
    }}
    .drawer-panel::-webkit-scrollbar-thumb {{
        background: rgba(139, 92, 246, 0.3);
        border-radius: 10px;
    }}
    #drawer-toggle {{ display: none; }}
    #drawer-toggle:checked ~ .drawer-panel {{ left: 0; }}
    #drawer-toggle:checked ~ .drawer-overlay {{ opacity: 1; visibility: visible; }}
.feature-item {{
display: flex;
align-items: center;
padding: 1rem;
margin-bottom: 0.8rem;
background: rgba(255, 255, 255, 0.03);
border: 1px solid rgba(255, 255, 255, 0.05);
border-radius: 16px;
transition: all 0.3s ease;
opacity: 0;
transform: translateX(-20px);
}}
    #drawer-toggle:checked ~ .drawer-panel .feature-item {{
        opacity: 1;
        transform: translateX(0);
    }}
.feature-item:hover {{
background: rgba(139, 92, 246, 0.1);
border-color: rgba(139, 92, 246, 0.3);
transform: translateX(10px);
}}
.feature-icon {{
width: 40px;
height: 40px;
background: rgba(139, 92, 246, 0.2);
border-radius: 10px;
display: flex;
align-items: center;
justify-content: center;
margin-right: 15px;
color: #a78bfa;
}}
@media (max-width: 768px) {{
.drawer-panel {{ width: 85%; left: -100%; }}
}}
</style>
<div id="drawer-container">
<input type="checkbox" id="drawer-toggle">
<label class="drawer-btn" for="drawer-toggle">
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
</label>
<label class="drawer-overlay" for="drawer-toggle"></label>
<div class="drawer-panel">
<div style="margin-bottom: 40px;">
<h2 style="font-family: 'Space Grotesk', sans-serif; margin: 0; background: linear-gradient(90deg, #a78bfa, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Phone Resale Pro</h2>
<p style="opacity: 0.5; font-size: 0.9rem; margin-top: 5px;">Platform Intelligence Features</p>
</div>
<div class="feature-item" style="transition-delay: 0.1s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v4.5"/><path d="M16 11l5 5-5 5"/><path d="M11 16h10"/></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">ML Price Prediction</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Random Forest Regressor Engine</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.2s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">5,000+ Records</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Deep Indian Market Insights</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.3s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Multi-Brand Support</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Apple, Samsung, Google & More</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.4s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Live Image Retrieval</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Automated Web Image Sourcing</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.5s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Instant Estimates</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Zero-Latency Computation</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.6s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="18" height="12" rx="2" ry="2"></rect><line x1="23" y1="13" x2="23" y2="11"></line><line x1="5" y1="10" x2="5" y2="14"></line><line x1="9" y1="10" x2="9" y2="14"></line></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Hardware Analytics</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Condition & Battery Bias</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.7s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Premium Dashboard</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Platinum Glassmorphism UI</div>
</div>
</div>
<div class="feature-item" style="transition-delay: 0.8s;">
<div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg></div>
<div>
<div style="font-weight: 600; font-size: 0.95rem;">Scalable Database</div>
<div style="font-size: 0.75rem; opacity: 0.4;">Ready for iPhone 17-18</div>
</div>
</div>
</div>
</div>
""",
    unsafe_allow_html=True,
)


# ── Utilities ──────────────────────────────────────────────────────────────────

# Fetch your credentials from the .env file
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# In-memory cache to prevent redundant API calls
_image_cache: dict = {}

_TRUSTED_DOMAINS = {
    "gsmarena.com", "apple.com", "samsung.com", "oneplus.com", "google.com",
    "mi.com", "xiaomi.com", "store.google.com", "motorola.com", "nokia.com",
    "vivo.com", "oppo.com", "realme.com", "iqoo.com", "nothing.tech",
    "honor.com", "asus.com", "sony.com", "htc.com", "tcl.com",
    "amazon.com", "amazon.in", "flipkart.com", "croma.com", "bestbuy.com",
    "reliancedigital.in", "vijaysales.com",
    "gadgets360.com", "91mobiles.com", "smartprix.com", "mysmartprice.com",
    "pricebaba.com", "fonearena.com", "gizmochina.com", "phoneradar.com",
    "digit.in", "techradar.com", "tomsguide.com", "cnet.com",
    "notebookcheck.net", "kimovil.com", "phonearena.com",
    "xda-developers.com", "androidauthority.com", "droidlife.com",
    "techadvisor.com", "pocket-lint.com", "indianexpress.com",
    "cdn.mos.cms.futurecdn.net", "m-cdn.phonearena.com",
    "fdn.gsmarena.com", "fdn2.gsmarena.com",
    "images-na.ssl-images-amazon.com", "m.media-amazon.com",
    "rukminim1.flixcart.com", "rukminim2.flixcart.com",
    "i.gadgets360cdn.com", "cdn.pocket-lint.com",
    "image.oppo.com", "image.realme.net",
    "static.tomsguide.com", "static.digit.in",
    "i01.appmifile.com",
    "freepik.com", "img.freepik.com",
    "istockphoto.com", "media.istockphoto.com",
    "pngimg.com", "pngwing.com",
}

_BLOCKED_PATH_WORDS = frozenset([
    "forum", "thread", "leak", "attach", "avatar", "profile",
    "meme", "wallpaper", "thumbnail", "placeholder", "18+", "nsfw",
    "adult", "xxx", "porn", "nude", "sexy",
])


def _domain_of(url: str) -> str:
    try:
        from urllib.parse import urlparse
        host = urlparse(url).hostname or ""
        return host.lower().removeprefix("www.")
    except Exception:
        return ""


def _is_trusted_url(url: str) -> bool:
    domain = _domain_of(url)
    if not domain:
        return False
    parts = domain.split(".")
    for i in range(len(parts) - 1):
        candidate = ".".join(parts[i:])
        if candidate in _TRUSTED_DOMAINS:
            path_lower = url.lower()
            if any(w in path_lower for w in _BLOCKED_PATH_WORDS):
                return False
            return True
    return False


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_phone_image(brand: str, model: str) -> str:
    """Fetch an official product image URL with a multi-layered hybrid architecture:
    
    1. Try Serper.dev API (Bulletproof Google Image Search).
    2. Fallback: Try DuckDuckGo Image Search (using ddgs) with premium brand filters.
    3. Final Fallback: Return a premium glassmorphic vector SVG.
    """
    brand_str = str(brand).strip()
    model_str = str(model).strip()
    cache_key = f"{brand_str}|{model_str}".lower()

    # Explicit override for iPhone 12 Pro to guarantee a high-quality, verified transparent image
    if brand_str.lower() == "apple" and model_str.lower() == "iphone 12 pro":
        return "https://pngimg.com/uploads/iphone_12/iphone_12_PNG20.png"

    if cache_key in _image_cache:
        return _image_cache[cache_key]

    # Pipeline 1: Serper.dev Search (Primary)
    if SERPER_API_KEY:
        try:
            import json
            search_query = f"{brand_str} {model_str} smartphone official stock product shot transparent background"
            url = "https://google.serper.dev/images"
            payload = json.dumps({"q": search_query})
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload, timeout=4)
            if response.status_code == 200:
                data = response.json()
                images = data.get("images", [])
                if images:
                    img_url = ""
                    # First try to find a trusted URL
                    for img in images:
                        cand = img.get("imageUrl", "")
                        if cand and _is_trusted_url(cand):
                            img_url = cand
                            break
                    # If not found, filter out mockups and templates
                    if not img_url:
                        for img in images:
                            cand = img.get("imageUrl", "")
                            if cand and not any(w in cand.lower() for w in ["mockup", "template", "dummy"]):
                                img_url = cand
                                break
                    # Fallback to first image
                    if not img_url:
                        img_url = images[0].get("imageUrl", "")
                        
                    if img_url:
                        _image_cache[cache_key] = img_url
                        return img_url
        except Exception:
            pass

    # Pipeline 2: DuckDuckGo Search (ddgs)
    if DDGS is not None:
        try:
            ddg_query = f"{brand_str} {model_str} smartphone official product image white background"
            with DDGS() as ddgs:
                results = ddgs.images(ddg_query, max_results=10, safesearch="strict")
                if results:
                    img_url = ""
                    # Look for trusted domains first
                    for r in results:
                        cand = r.get("image", "")
                        if cand and _is_trusted_url(cand):
                            img_url = cand
                            break
                    # If not found, filter out mockups and templates
                    if not img_url:
                        for r in results:
                            cand = r.get("image", "")
                            if cand and not any(w in cand.lower() for w in ["mockup", "template", "dummy"]):
                                img_url = cand
                                break
                    # Otherwise, use the first result if available
                    if not img_url:
                        img_url = results[0].get("image", "")
                    if img_url:
                        _image_cache[cache_key] = img_url
                        return img_url
        except Exception:
            pass

    # Pipeline 3: Glassmorphism SVG fallback
    svg = _generate_svg_placeholder(brand_str, model_str)
    _image_cache[cache_key] = svg
    return svg


def _generate_svg_placeholder(brand: str, model: str) -> str:
    """Generate a premium dark-glassmorphism SVG data URI showing Brand + Model."""
    safe_brand = brand.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_model = model.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" width="400" height="480">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0c0e18"/>
      <stop offset="50%" stop-color="#111327"/>
      <stop offset="100%" stop-color="#0a0c14"/>
    </linearGradient>
    <linearGradient id="border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(139,92,246,0.6)"/>
      <stop offset="50%" stop-color="rgba(99,102,241,0.25)"/>
      <stop offset="100%" stop-color="rgba(96,165,250,0.4)"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#60a5fa"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="orb1" cx="30%" cy="25%">
      <stop offset="0%" stop-color="rgba(139,92,246,0.15)"/>
      <stop offset="100%" stop-color="transparent"/>
    </radialGradient>
    <radialGradient id="orb2" cx="75%" cy="80%">
      <stop offset="0%" stop-color="rgba(96,165,250,0.10)"/>
      <stop offset="100%" stop-color="transparent"/>
    </radialGradient>
  </defs>

  <rect width="400" height="480" rx="28" fill="url(#bg)"/>
  <rect width="400" height="480" rx="28" fill="none" stroke="url(#border)" stroke-width="1.5"/>
  <circle cx="120" cy="120" r="160" fill="url(#orb1)"/>
  <circle cx="300" cy="380" r="120" fill="url(#orb2)"/>
  <rect x="130" y="60" width="140" height="260" rx="18" fill="none" stroke="rgba(139,92,246,0.25)" stroke-width="1.5" filter="url(#glow)"/>
  <rect x="130" y="60" width="140" height="260" rx="18" fill="rgba(255,255,255,0.02)"/>
  <circle cx="200" cy="85" r="6" fill="none" stroke="rgba(139,92,246,0.35)" stroke-width="1"/>
  <rect x="140" y="100" width="120" height="190" rx="4" fill="rgba(139,92,246,0.04)" stroke="rgba(139,92,246,0.1)" stroke-width="0.5"/>
  <text x="200" y="370" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-weight="700" font-size="22" fill="url(#accent)" letter-spacing="1">{safe_brand}</text>
  <text x="200" y="405" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-weight="400" font-size="16" fill="#94a3b8" letter-spacing="0.5">{safe_model}</text>
  <text x="200" y="448" text-anchor="middle" font-family="system-ui,-apple-system,sans-serif" font-weight="300" font-size="10" fill="rgba(148,163,184,0.4)" letter-spacing="2">IMAGE PLACEHOLDER</text>
</svg>'''

    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def render_phone_visual(brand: str, model: str) -> str:
    """Return the full HTML block to render the phone image card frame layout."""
    img_src = fetch_phone_image(brand, model)
    is_svg = img_src.startswith("data:")
    img_style = "width:100%; border-radius:16px;"
    
    # Standard security fallback: if an external site blocks cross-origin image requests
    # it catches the error and breaks to a blank space gracefully instead of an ugly broken icon
    onerror = "" if is_svg else " onerror=\"this.src='';this.style.display='none'\""
    return (
        f'<div class="phone-visual-card">'
        f'<img src="{img_src}" style="{img_style}" alt="{brand} {model}"{onerror}>'
        f'</div>'
    )


def create_styled_chart(months, prices):
    """Create a premium, futuristic Plotly line chart."""
    fig = go.Figure()

    # Add the primary line with a subtle glow effect (overlapping lines)
    fig.add_trace(
        go.Scatter(
            x=months,
            y=prices,
            mode="lines+markers",
            line=dict(color="#60a5fa", width=5, shape="spline"),
            marker=dict(size=10, color="#1e293b", line=dict(width=2, color="#60a5fa")),
            hoverinfo="text",
            text=[f"Month {m}: ₹ {p:,.0f}" for m, p in zip(months, prices)],
            name="Value Forecast",
        )
    )

    # Add a glowing overlay line
    fig.add_trace(
        go.Scatter(
            x=months,
            y=prices,
            mode="lines",
            line=dict(color="rgba(96, 165, 250, 0.3)", width=12, shape="spline"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=20, b=0),
        showlegend=False,
        height=300,
        xaxis=dict(
            showgrid=True,
            gridcolor="#334155",
            tickfont=dict(color="#94a3b8"),
            title=dict(text="Months", font=dict(color="#64748b", size=12)),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#334155",
            tickfont=dict(color="#94a3b8"),
            tickprefix="₹ ",
            title=dict(text="Estimated Value", font=dict(color="#64748b", size=12)),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_family="Outfit"),
    )
    return fig


# ── Load artifacts & Data ──────────────────────────────────────────────────────
try:
    model_obj, encoders = load_artifacts()
    data_path = os.path.join(os.path.dirname(__file__), "data", "used_phones_clean.csv")
    df_raw = pd.read_csv(data_path)
    variants_path = os.path.join(
        os.path.dirname(__file__), "data", "phone_variants.csv"
    )
    variants_df = pd.read_csv(variants_path)
    # Robust normalization: remove spaces and handle case-insensitive lookups later
    variants_df["brand_clean"] = (
        variants_df["brand"].astype(str).str.strip().str.lower()
    )
    variants_df["model_clean"] = (
        variants_df["model"].astype(str).str.strip().str.lower()
    )

    brand_model_map = (
        variants_df.groupby("brand")["model"].unique().apply(list).to_dict()
    )

    brands = sorted(brand_model_map.keys())

    # Keep launch prices from training data
    model_price_map = df_raw.groupby("model")["launch_price"].median().to_dict()
    conditions = sorted(
        get_known_conditions(encoders),
        key=lambda x: ["Excellent", "Good", "Fair", "Poor"].index(x),
    )
except Exception as e:
    st.error(f"System Error: {e}")
    st.stop()


# ── Hero Section ──────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
<div class="hero-container fade-in hidden lg:block">
<div class="hero-glass-card" style="background-color: rgba(10, 15, 25, 0.4); background-image: url(data:image/jpeg;base64,{{nebula_b64}}); background-size: cover; background-position: center; background-blend-mode: overlay;">

<!-- Premium PC Hero Background Effects Array -->
<div style="position: absolute; inset: 0; overflow: hidden; border-radius: 28px; z-index: 0; pointer-events: none;">
<div class="hero-grid-bg"></div>
<div class="hero-orb-1"></div>
<div class="hero-orb-2" style="bottom: -80px;"></div>
<div class="hero-scanline"></div>
</div>

<div class="z-10 flex flex-col w-7/12 md:w-3/5 lg:w-3/5" style="position: relative; padding-top: 15px;">
<div class="hero-badge" style="width: max-content; margin-bottom: 8px;">
<div class="hero-badge-dot"></div>
<span style="font-family: 'DM Sans', sans-serif;">India Market Intelligence</span>
</div>

<h1 class="hero-title font-bold tracking-tighter mb-0" style="margin-top: -4px;">
Phone <span class="hero-title-accent" style="display:inline-block;">Resale</span> Pro
</h1>

<p class="hero-subtitle text-slate-300 font-light tracking-wide mb-4">
Smart AI price estimates for every used phone's true market value.
</p>

<!-- Stats Configuration (PC Scale) -->
<div class="hero-stats" style="margin-top: 5px;">
<div class="hero-stat"><span class="hero-stat-val">5K+</span><span class="hero-stat-lbl">Records</span></div>
<div class="hero-stat"><span class="hero-stat-val">50+</span><span class="hero-stat-lbl">Brands</span></div>
<div class="hero-stat"><span class="hero-stat-val">98%</span><span class="hero-stat-lbl">Accuracy</span></div>
</div>
</div>

<!-- Phone Images Cluster -->
<img src="data:image/png;base64,{iphone_b64}" class="iphone-overlay">
<img src="data:image/png;base64,{samsung_b64}" class="samsung-overlay">

</div>
</div>

<!-- Mobile Hero Layout -->
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&display=swap');

.hero-mobile-wrap {{
width: 92%;
max-width: 430px;
margin: 1.5rem auto 2rem auto;
position: relative;
border-radius: 28px;
overflow: hidden;
background: #050709;
min-height: 400px;
font-family: 'DM Sans', sans-serif;
}}

.hero-border-ring {{
position: absolute; inset: 0;
border-radius: 28px;
border: 1.5px solid transparent;
background: linear-gradient(135deg, rgba(139,92,246,0.6), rgba(99,102,241,0.2), rgba(139,92,246,0.08), rgba(96,165,250,0.3)) border-box;
-webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
-webkit-mask-composite: destination-out;
mask-composite: exclude;
pointer-events: none; z-index: 10;
}}

.hero-grid-bg {{
position: absolute; inset: 0; z-index: 1;
opacity: 0.025; pointer-events: none;
background-image:
linear-gradient(rgba(139,92,246,1) 1px, transparent 1px),
linear-gradient(90deg, rgba(139,92,246,1) 1px, transparent 1px);
background-size: 40px 40px;
border-radius: 28px;
}}

.hero-orb-1 {{
position: absolute; width: 280px; height: 280px;
border-radius: 50%;
background: radial-gradient(circle, rgba(99,102,241,0.22) 0%, transparent 70%);
top: -80px; right: -60px; pointer-events: none; z-index: 0;
}}

.hero-orb-2 {{
position: absolute; width: 200px; height: 200px;
border-radius: 50%;
background: radial-gradient(circle, rgba(139,92,246,0.14) 0%, transparent 70%);
bottom: -40px; left: -20px; pointer-events: none; z-index: 0;
}}

.hero-scanline {{
position: absolute; left: 0; right: 0; height: 1px;
background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), transparent);
animation: heroScan 4s ease-in-out infinite;
z-index: 2; pointer-events: none;
}}
@keyframes heroScan {{
0%   {{ top: 0%; opacity: 0; }}
10%  {{ opacity: 1; }}
90%  {{ opacity: 1; }}
100% {{ top: 100%; opacity: 0; }}
}}

.hero-content {{
position: relative; z-index: 5;
padding: 28px 24px 0 17px;
}}

.hero-badge {{
display: inline-flex; align-items: center; gap: 6px;
background: rgba(139,92,246,0.12);
border: 1px solid rgba(139,92,246,0.3);
border-radius: 100px;
padding: 5px 12px;
font-size: 11px; font-weight: 500; color: #a78bfa;
letter-spacing: 0.08em; text-transform: uppercase;
margin-bottom: 18px;
animation: heroFadeUp 0.6s ease-out both;
}}

.hero-badge-dot {{
width: 5px; height: 5px; border-radius: 50%;
background: #8b5cf6;
box-shadow: 0 0 6px rgba(139,92,246,0.8);
animation: heroPulse 1.8s ease-in-out infinite;
}}
@keyframes heroPulse {{
0%, 100% {{ opacity: 1; transform: scale(1); }}
50% {{ opacity: 0.5; transform: scale(0.7); }}
}}

.hero-title {{
font-family: 'Syne', sans-serif;
font-weight: 800; font-size: 44px;
line-height: 0.95; letter-spacing: -2px;
color: #f1f5f9; margin: 0;
animation: heroFadeUp 0.7s 0.1s ease-out both;
}}

.hero-title-accent {{
display: block;
background: linear-gradient(90deg, #818cf8, #a78bfa, #60a5fa);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
background-clip: text;
}}

.hero-sub {{
font-size: 13px; line-height: 1.55; color: #64748b;
margin-top: 12px; max-width: 220px; font-weight: 400;
animation: heroFadeUp 0.7s 0.2s ease-out both;
}}

.hero-stats {{
display: flex; gap: 5px; margin-top: 20px;
animation: heroFadeUp 0.7s 0.3s ease-out both;
}}

.hero-stat {{
background: rgba(255,255,255,0.03);
border: 1px solid rgba(255,255,255,0.07);
border-radius: 12px; padding: 10px 14px;
display: flex; flex-direction: column; gap: 2px;
}}

.hero-stat-val {{
font-family: 'Syne', sans-serif;
font-size: 15px; font-weight: 700; color: #e2e8f0;
}}

.hero-stat-lbl {{
font-size: 9px; color: #475569; font-weight: 400;
letter-spacing: 0.05em; text-transform: uppercase;
}}

.hero-phones {{
position: relative; width: 100%; height: 210px;
margin-top: 8px;
animation: heroFadeUp 0.8s 0.35s ease-out both;
}}

.phone-glow-shadow {{
position: absolute; bottom: 8px;
height: 16px; border-radius: 50%;
background: rgba(99,102,241,0.2); filter: blur(10px);
}}

.iphone-phone {{
position: absolute; left: 14px; bottom: 16px; z-index: 6;
transform: rotate(-12deg);
animation: heroFloatL 4s ease-in-out infinite;
filter: drop-shadow(0 20px 40px rgba(0,0,0,0.7)) drop-shadow(0 0 18px rgba(99,102,241,0.25));
}}
@keyframes heroFloatL {{
0%, 100% {{ transform: rotate(-12deg) translateY(0px); }}
50%       {{ transform: rotate(-12deg) translateY(-10px); }}
}}

.samsung-phone {{
position: absolute; right: -18px; bottom: 0; z-index: 7;
transform: rotate(8deg);
animation: heroFloatR 5s ease-in-out infinite;
filter: drop-shadow(0 20px 40px rgba(0,0,0,0.7)) drop-shadow(0 0 14px rgba(96,165,250,0.2));
}}
@keyframes heroFloatR {{
0%, 100% {{ transform: rotate(8deg) translateY(0px); }}
50%       {{ transform: rotate(8deg) translateY(-8px); }}
}}

.hero-bottom-bar {{
position: absolute; bottom: 0; left: 0; right: 0;
z-index: 8; padding: 14px 22px;
display: flex; align-items: center; justify-content: space-between;
background: linear-gradient(to top, rgba(5,7,9,0.95) 0%, transparent 100%);
animation: heroFadeUp 0.8s 0.45s ease-out both;
}}

.hero-bottom-label {{
font-size: 10px; color: #475569; font-weight: 400;
letter-spacing: 0.04em; text-transform: uppercase;
}}

@keyframes heroFadeUp {{
from {{ opacity: 0; transform: translateY(16px); }}
to   {{ opacity: 1; transform: translateY(0); }}
}}
</style>

<div class="block lg:hidden hero-mobile-wrap">
<div class="hero-grid-bg"></div>
<div class="hero-orb-1"></div>
<div class="hero-orb-2"></div>
<div class="hero-scanline"></div>
<div class="hero-border-ring"></div>

<div class="hero-content">
<div class="hero-badge">
<div class="hero-badge-dot"></div>
India Market Intelligence
</div>
<h1 class="hero-title">
Phone
<span class="hero-title-accent">Resale</span>
Pro
</h1>
<p class="hero-sub">Smart AI price estimates for every used phone's true market value.</p>
<div class="hero-stats">
<div class="hero-stat">
<span class="hero-stat-val">5K+</span>
<span class="hero-stat-lbl">Records</span>
</div>
<div class="hero-stat">
<span class="hero-stat-val">50+</span>
<span class="hero-stat-lbl">Brands</span>
</div>
<div class="hero-stat">
<span class="hero-stat-val">98%</span>
<span class="hero-stat-lbl">Accuracy</span>
</div>
</div>
</div>

<div class="hero-phones">
<div class="phone-glow-shadow" style="left:24px; width:80px;"></div>
<div class="phone-glow-shadow" style="right:16px; width:60px;"></div>

<img src="data:image/png;base64,{iphone_b64}" class="iphone-phone" style="height:158px;">
<img src="data:image/png;base64,{samsung_b64}" class="samsung-phone" style="height:210px;">
</div>

</div>

""",
    unsafe_allow_html=True,
)


def mobile_selector(label, options, key):
    if key not in st.session_state or st.session_state[key] is None:
        st.session_state[key] = options[0] if options else ""

    selected = str(st.session_state[key] or "")

    st.markdown(
        f"<p style=\"font-family: 'Outfit', sans-serif; font-weight: 400; color: #94a3b8; font-size: 0.95rem; letter-spacing: 0.025em; margin-bottom: 0.5rem;\">{label}</p>",
        unsafe_allow_html=True,
    )

    with st.popover(selected, use_container_width=True):
        search_enabled = st.toggle("🔎 Search", key=f"{key}_search_toggle")

        if search_enabled:
            query = st.text_input("Type to search", key=f"{key}_search_input")
            filtered_options = [
                opt for opt in options if query.lower() in str(opt).lower()
            ]
        else:
            filtered_options = options

        for option_index, opt in enumerate(filtered_options):
            button_key = f"{key}_option_{option_index}"
            if st.button(str(opt), key=button_key, use_container_width=True):
                st.session_state[key] = opt
                st.rerun()

    return st.session_state[key]


# ── Main Layout ───────────────────────────────────────────────────────────────
main_col1, main_col2 = st.columns([1, 1.2], gap="large")

with main_col1:

    brand = mobile_selector("📌 Select Brand", brands, "selected_brand")
    brand = str(brand or "")

    brand_models = sorted(brand_model_map.get(brand, []))

    if st.session_state.get("last_brand") != brand:
        st.session_state["selected_model"] = brand_models[0] if brand_models else ""
        st.session_state["last_brand"] = brand

    with st.container():

        st.subheader("📱 Device Configuration")

        model_name = mobile_selector("Specific Model", brand_models, "selected_model")
        model_name = str(model_name or "")

        c1, c2 = st.columns(2)

        with c1:

            brand_clean = brand.strip().lower()
            model_name_clean = model_name.strip().lower()

            def is_match(csv_model):
                csv_model = str(csv_model)

                if csv_model == model_name_clean:
                    return True

                if (brand_clean + " " + csv_model) == model_name_clean:
                    return True

                if (
                    brand_clean == "motorola"
                    and ("moto " + csv_model) == model_name_clean
                ):
                    return True

                return False

            model_variants = variants_df[
                (variants_df["brand_clean"] == brand_clean)
                & (variants_df["model_clean"].apply(is_match))
            ]

            ram_options = (
                sorted(model_variants["ram"].unique())
                if not model_variants.empty
                else [2, 4, 6, 8, 12, 16]
            )

            ram = st.selectbox("RAM (GB)", options=ram_options)

            storage_options = (
                sorted(model_variants[model_variants["ram"] == ram]["rom"].unique())
                if not model_variants.empty
                else [32, 64, 128, 256, 512]
            )

            storage = st.selectbox("Storage (GB)", options=storage_options)

        with c2:

            age_months = st.slider("Phone Age (Months)", 1, 60, 12)

            battery = st.slider("Battery Health %", 50, 100, 90)

        condition = st.selectbox("Visual Condition", options=conditions)

    predict_clicked = st.button(
        "ANALYZE MARKET VALUE", type="primary", use_container_width=True
    )


with main_col2:
    if predict_clicked:
        spinner_messages = [
            "Analyzing resale trends...",
            "Evaluating current market demand...",
            "Generating smart estimate...",
            "Calculating fair resale value...",
        ]
        with st.spinner(random.choice(spinner_messages)):

            matching_variant = variants_df[
                (variants_df["brand_clean"] == brand_clean)
                & (variants_df["model_clean"].apply(is_match))
                & (variants_df["ram"] == ram)
                & (variants_df["rom"] == storage)
            ]

            if (
                not matching_variant.empty
                and "launch_price" in matching_variant.columns
            ):
                variant_price = matching_variant.iloc[0]["launch_price"]

                if pd.notna(variant_price):
                    launch_price = float(variant_price)
                else:
                    launch_price = model_price_map.get(model_name, 25000)

            else:
                launch_price = model_price_map.get(model_name, 25000)

            price = predict_price(
                model_obj=model_obj,
                encoders=encoders,
                brand=brand,
                model_name=model_name,
                ram_gb=ram,
                storage_gb=storage,
                age_months=age_months,
                battery_health=battery,
                condition=condition,
                launch_price=launch_price,
            )

            low, high = price * 0.92, price * 1.08

            st.markdown(
                f"""
<div class="result-box">
<div class="label-text">Current Market Value</div>
<div class="price-value">₹ {price:,.0f}</div>
<div class="info-tag">Launch Price: ₹ {launch_price:,.0f}</div>
<div class="info-tag">Retention: {price/launch_price*100:.1f}%</div>
<p style="margin-top:1.2rem; opacity:0.6; font-size:0.95rem;">
Suggested Range: <b>₹ {low:,.0f} - ₹ {high:,.0f}</b>
</p>
</div>
""",
                unsafe_allow_html=True,
            )

            res1, res2 = st.columns([1, 1.8])
            with res1:
                st.markdown(
                    render_phone_visual(brand, model_name),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='text-align:center; opacity:0.6; font-size:0.8rem;'>{model_name}</p>",
                    unsafe_allow_html=True,
                )

            with res2:
                with st.container():
                    st.markdown("### 📈 Lifecycle Forecast")
                    # Calculate future values (4% monthly drop for mock forecast)
                    months_f = list(range(age_months, age_months + 25, 4))
                    future_prices = [
                        price * (0.96 ** (m - age_months)) for m in months_f
                    ]

                    fig = create_styled_chart(months_f, future_prices)
                    st.plotly_chart(
                        fig, use_container_width=True, config={"displayModeBar": False}
                    )
                    st.caption("Forecasted market value over the next 24 months")
    else:
        st.markdown(
            """
        <div style="text-align:center; padding: 6rem 2rem; opacity:0.15;">
            <div style="font-size: 80px; text-shadow: 0 0 30px rgba(96, 165, 250, 1);">📈</div><br>
            <h3 style="margin-top:1.5rem;">Analytical Engine Idle</h3>
            <p>Select your hardware parameters to initiate resale forecasting.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="footer">
Phone Resale Pro v1.0 • Smart Estimates Powered by 5K+ Market Records •
Built by Sayak Bhattasali •
<a href="https://github.com/sayakbhattasali" target="_blank">GitHub</a>
</div>
""",
    unsafe_allow_html=True,
)

