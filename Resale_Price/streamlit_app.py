"""
streamlit_app.py
----------------
Smartphone Resale Price Predictor – DeviceValue AI Design System Edition.
Seamlessly matched with DeviceValue AI's cyber-clean navy & violet aesthetic.

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
import urllib.parse
import re
from dotenv import load_dotenv
try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

# Make sure project directory is importable
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
st.set_page_config(
    page_title="DeviceValue AI — Smartphone Resale Valuation",
    page_icon="📱",
    layout="wide",
)

# ── Asset Preparation ────────────────────────────────────────────────────────
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

# ── DeviceValue AI Design System Theme Injection ──────────────────────────────
st.markdown(
    f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Instrument+Sans:wght@500;600;700&display=swap');

    :root {{
        --font-sans: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        --font-display: 'Instrument Sans', 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        --navy-950: #0a0e1a;
        --navy-900: #0f1629;
        --navy-800: #151d35;
        --navy-700: #1c2744;
        --accent-blue: #3b82f6;
        --accent-blue-hover: #2563eb;
        --accent-violet: #8b5cf6;
        --accent-violet-hover: #7c3aed;
        --text-main: #f1f5f9;
        --text-muted: #94a3b8;
        --text-sub: #64748b;
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-focus: rgba(59, 130, 246, 0.6);
    }}

    /* Global Body & Background matching DeviceValue AI */
    .stApp {{
        background-color: var(--navy-950) !important;
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.15), transparent),
            radial-gradient(ellipse 60% 40% at 100% 0%, rgba(139, 92, 246, 0.12), transparent),
            radial-gradient(ellipse 50% 30% at 0% 50%, rgba(59, 130, 246, 0.08), transparent) !important;
        background-attachment: fixed !important;
        color: var(--text-main) !important;
        font-family: var(--font-sans) !important;
        -webkit-font-smoothing: antialiased;
    }}

    ::selection {{
        background: rgba(59, 130, 246, 0.35) !important;
        color: #ffffff !important;
    }}

    /* Hide Default Streamlit Clutter */
    #MainMenu {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    [data-testid="stHeader"] {{ display: none; }}
    [data-testid="stToolbar"] {{ display: none; }}
    [data-testid="stDecoration"] {{ display: none; }}
    [data-testid="stStatusWidget"] {{ display: none; }}

    /* Layout Spacing */
    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 4rem !important;
        max-width: 1240px !important;
    }}

    /* Typography Utilities */
    .font-display {{
        font-family: var(--font-display) !important;
    }}

    /* Top Navigation Bar */
    .nav-bar-container {{
        position: sticky;
        top: 0;
        z-index: 99990;
        background: rgba(10, 14, 26, 0.85);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--border-subtle);
        margin: -1.5rem -1rem 1.5rem -1rem;
        padding: 0.85rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .nav-brand {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        text-decoration: none;
    }}
    .nav-logo-badge {{
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 12px;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    }}
    .nav-title {{
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 1.15rem;
        color: #ffffff;
        letter-spacing: -0.02em;
    }}
    .nav-title-accent {{
        color: #60a5fa;
    }}
    .nav-tag {{
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 9999px;
        font-size: 0.7rem;
        font-weight: 600;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #93c5fd;
        margin-left: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .nav-links {{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }}
    .nav-link-btn {{
        font-family: var(--font-sans);
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-muted);
        background: transparent;
        border: none;
        cursor: pointer;
        transition: color 0.2s ease;
        text-decoration: none;
    }}
    .nav-link-btn:hover {{
        color: #ffffff;
    }}
    .nav-cta-pill {{
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: #ffffff !important;
        border-radius: 10px;
        padding: 0.45rem 1rem;
        font-size: 0.82rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}
    .nav-cta-pill:hover {{
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.45);
        transform: translateY(-1px);
    }}

    /* Hero Section (DeviceValue AI Clean Glass Theme) */
    .hero-container {{
        width: 100%;
        margin-bottom: 2rem;
        position: relative;
    }}
    .hero-card {{
        position: relative;
        width: 100%;
        border-radius: 24px;
        border: 1px solid var(--border-subtle);
        background: rgba(15, 22, 41, 0.55);
        backdrop-filter: blur(24px);
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04), 0 20px 40px -15px rgba(0, 0, 0, 0.5), 0 0 50px rgba(59, 130, 246, 0.05);
        padding: 2.5rem 3rem;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .hero-content {{
        position: relative;
        z-index: 10;
        max-width: 620px;
    }}
    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 9999px;
        padding: 0.3rem 0.85rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #93c5fd;
        margin-bottom: 1rem;
        letter-spacing: 0.02em;
    }}
    .hero-badge-dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #3b82f6;
        box-shadow: 0 0 8px #3b82f6;
    }}
    .hero-title {{
        font-family: var(--font-display);
        font-size: clamp(2.2rem, 4vw, 3.25rem);
        font-weight: 700;
        color: #ffffff;
        line-height: 1.15;
        letter-spacing: -0.03em;
        margin: 0;
    }}
    .hero-title-accent {{
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .hero-subtitle {{
        font-size: 1rem;
        line-height: 1.6;
        color: var(--text-muted);
        margin-top: 0.75rem;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }}
    .hero-stats {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
    }}
    .hero-stat-pill {{
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 12px;
        padding: 0.45rem 0.85rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.82rem;
    }}
    .hero-stat-val {{
        font-family: var(--font-display);
        font-weight: 700;
        color: #ffffff;
    }}
    .hero-stat-lbl {{
        color: var(--text-sub);
    }}
    .hero-visual-col {{
        position: relative;
        width: 320px;
        height: 240px;
        display: none;
    }}
    @media (min-width: 992px) {{
        .hero-visual-col {{ display: block; }}
    }}
    .hero-halo {{
        position: absolute;
        inset: -20px;
        background: radial-gradient(circle at 60% 50%, rgba(59, 130, 246, 0.22), rgba(139, 92, 246, 0.1) 50%, transparent 70%);
        filter: blur(20px);
        pointer-events: none;
    }}
    .iphone-overlay-card {{
        position: absolute;
        top: 10px;
        right: 90px;
        height: 190px;
        z-index: 10;
        filter: drop-shadow(0 20px 30px rgba(0, 0, 0, 0.6));
        transform: rotate(-9deg);
        animation: floatPhoneL 5s ease-in-out infinite;
    }}
    .samsung-overlay-card {{
        position: absolute;
        top: -10px;
        right: 0;
        height: 230px;
        z-index: 11;
        filter: drop-shadow(0 25px 35px rgba(0, 0, 0, 0.7));
        transform: rotate(7deg);
        animation: floatPhoneR 6s ease-in-out infinite;
    }}
    @keyframes floatPhoneL {{
        0%, 100% {{ transform: rotate(-9deg) translateY(0); }}
        50% {{ transform: rotate(-9deg) translateY(-8px); }}
    }}
    @keyframes floatPhoneR {{
        0%, 100% {{ transform: rotate(7deg) translateY(0); }}
        50% {{ transform: rotate(7deg) translateY(-10px); }}
    }}

    /* Card Panels & Containers */
    .card-glow {{
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.06), 0 4px 24px rgba(0, 0, 0, 0.35), 0 0 40px rgba(59, 130, 246, 0.04) !important;
    }}
    [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"] {{
        background: rgba(21, 29, 53, 0.5) !important;
        border-radius: 20px !important;
        border: 1px solid var(--border-subtle) !important;
        backdrop-filter: blur(20px) !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04), 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 30px rgba(59, 130, 246, 0.03) !important;
        padding: 2rem !important;
        margin-bottom: 1rem !important;
        transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
    }}
    [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:hover {{
        border-color: rgba(59, 130, 246, 0.25) !important;
    }}

    /* Section Subheadings */
    h3, [data-testid="stHeadingWithActionElements"] h3 {{
        font-family: var(--font-display) !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        color: #ffffff !important;
        letter-spacing: -0.01em !important;
        margin-bottom: 0.75rem !important;
    }}

    /* Label Styling */
    label[data-testid="stWidgetLabel"] p, .custom-field-label {{
        font-family: var(--font-sans) !important;
        font-weight: 500 !important;
        color: var(--text-main) !important;
        font-size: 0.875rem !important;
        letter-spacing: 0.01em !important;
        margin-bottom: 0.4rem !important;
    }}

    /* Selectboxes: DeviceValue AI Input Field Styling */
    div[data-testid="stSelectbox"] > div {{
        background: rgba(15, 22, 41, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        height: 48px !important;
        font-family: var(--font-sans) !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }}
    div[data-testid="stSelectbox"] > div:hover,
    div[data-testid="stSelectbox"] > div:focus-within {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18) !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"] span {{
        color: #ffffff !important;
        font-size: 0.875rem !important;
    }}

    /* Custom Popover Selectors: Match DeviceValue AI SearchableSelect */
    [data-testid="stPopover"] > div {{
        background-color: var(--navy-900) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.06) !important;
        backdrop-filter: blur(20px) !important;
        color: var(--text-main) !important;
    }}
    [data-testid="stPopover"] button {{
        background: rgba(15, 22, 41, 0.85) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        min-height: 48px !important;
        padding: 0 1rem !important;
        font-family: var(--font-sans) !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 2px 6px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}
    [data-testid="stPopover"] button:hover,
    [data-testid="stPopover"] button:focus {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18) !important;
        outline: none !important;
        background: rgba(21, 29, 53, 0.95) !important;
    }}

    /* Slider Overhaul */
    div[data-testid="stSlider"] {{
        padding-top: 0.75rem !important;
        padding-bottom: 0.75rem !important;
    }}
    .stSlider [data-baseweb="slider"] {{
        background: transparent !important;
    }}
    .stSlider [role="slider"] {{
        background-color: var(--accent-blue) !important;
        box-shadow: 0 0 12px rgba(59, 130, 246, 0.6) !important;
        border: 2px solid #ffffff !important;
        width: 18px !important;
        height: 18px !important;
    }}

    /* Primary CTA Button: DeviceValue AI Signature Gradient */
    button[kind="primary"] {{
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        font-family: var(--font-sans) !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        letter-spacing: 0.02em !important;
        color: #ffffff !important;
        padding: 0.85rem 1.75rem !important;
        box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.35) !important;
        transition: all 0.25s ease !important;
        margin-top: 0.5rem !important;
    }}
    button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        box-shadow: 0 12px 25px -4px rgba(37, 99, 235, 0.5) !important;
        transform: translateY(-1px) !important;
    }}

    /* Product Information Card */
    .product-info-card {{
        background: rgba(21, 29, 53, 0.55) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.04), 0 10px 30px -10px rgba(0, 0, 0, 0.5), 0 0 30px rgba(59, 130, 246, 0.03) !important;
        backdrop-filter: blur(20px) !important;
        transition: border-color 0.25s ease !important;
    }}
    .product-info-card:hover {{
        border-color: rgba(59, 130, 246, 0.25) !important;
    }}
    .product-header {{
        margin-bottom: 0.85rem;
    }}
    .product-header-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 9999px;
        padding: 0.2rem 0.65rem;
        font-size: 0.72rem;
        font-weight: 600;
        color: #93c5fd;
        margin-bottom: 0.45rem;
    }}
    .product-title {{
        font-family: var(--font-display) !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin: 0 !important;
        line-height: 1.2 !important;
    }}
    .product-sub {{
        font-size: 0.8rem !important;
        color: var(--text-sub) !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0 !important;
    }}

    /* Result Card Presentation */
    .result-card {{
        background: rgba(21, 29, 53, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 20px !important;
        padding: 2rem !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.06), 0 12px 32px -8px rgba(0, 0, 0, 0.5), 0 0 40px rgba(59, 130, 246, 0.04) !important;
        backdrop-filter: blur(20px) !important;
        margin-bottom: 1.5rem !important;
    }}
    .result-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 9999px;
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 600;
        color: #93c5fd;
        margin-bottom: 0.85rem;
    }}
    .result-label {{
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}
    .result-price {{
        font-family: var(--font-display);
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.03em;
        line-height: 1.05;
        margin-bottom: 0.5rem;
    }}
    .result-subtext {{
        font-size: 0.75rem;
        color: var(--text-sub);
        margin-bottom: 1.5rem;
    }}
    .spec-table {{
        display: flex;
        flex-direction: column;
        border-top: 1px solid var(--border-subtle);
        padding-top: 0.75rem;
        gap: 0.6rem;
    }}
    .spec-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 0.85rem;
    }}
    .spec-label {{
        color: var(--text-sub);
    }}
    .spec-value {{
        font-weight: 600;
        color: var(--text-main);
    }}
    .spec-value-accent {{
        color: #60a5fa;
    }}

    /* Idle Card State */
    .idle-card {{
        background: rgba(21, 29, 53, 0.4) !important;
        border: 1px dashed rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        padding: 4.5rem 2rem !important;
        text-align: center;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.02) !important;
    }}
    .idle-icon-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 56px;
        height: 56px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15));
        border: 1px solid rgba(59, 130, 246, 0.25);
        color: #60a5fa;
        margin-bottom: 1rem;
    }}
    .idle-title {{
        font-family: var(--font-display);
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.4rem;
    }}
    .idle-sub {{
        font-size: 0.85rem;
        color: var(--text-sub);
        max-width: 320px;
        margin: 0 auto;
        line-height: 1.5;
    }}

    /* Phone Visual Card */
    .phone-visual-card {{
        background: rgba(21, 29, 53, 0.45);
        border: 1px solid var(--border-subtle);
        border-radius: 18px;
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 1rem;
        overflow: hidden;
    }}

    /* Side Intelligence Drawer (Polished to DeviceValue AI standard) */
    .drawer-btn {{
        position: fixed;
        bottom: 24px;
        left: 24px;
        z-index: 99999;
        background: rgba(15, 22, 41, 0.9);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #ffffff;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
    }}
    .drawer-btn:hover {{
        border-color: rgba(59, 130, 246, 0.6);
        box-shadow: 0 0 16px rgba(59, 130, 246, 0.4);
        transform: translateY(-2px);
    }}
    .drawer-overlay {{
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(6px);
        z-index: 999998;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
    }}
    .drawer-panel {{
        position: fixed;
        top: 0;
        left: -400px;
        width: 360px;
        height: 100vh;
        background: rgba(10, 14, 26, 0.96);
        backdrop-filter: blur(28px);
        border-right: 1px solid var(--border-subtle);
        z-index: 999999;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        padding: 40px 24px;
        display: flex;
        flex-direction: column;
        overflow-y: auto;
    }}
    #drawer-toggle {{ display: none; }}
    #drawer-toggle:checked ~ .drawer-panel {{ left: 0; }}
    #drawer-toggle:checked ~ .drawer-overlay {{ opacity: 1; visibility: visible; }}
    .drawer-title {{
        font-family: var(--font-display);
        font-weight: 700;
        font-size: 1.25rem;
        color: #ffffff;
        margin: 0;
    }}
    .drawer-sub {{
        font-size: 0.8rem;
        color: var(--text-sub);
        margin-top: 4px;
        margin-bottom: 24px;
    }}
    .feature-item {{
        display: flex;
        align-items: center;
        padding: 0.85rem;
        margin-bottom: 0.65rem;
        background: rgba(21, 29, 53, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        transition: all 0.2s ease;
    }}
    .feature-item:hover {{
        background: rgba(59, 130, 246, 0.1);
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateX(4px);
    }}
    .feature-icon {{
        width: 36px;
        height: 36px;
        background: rgba(59, 130, 246, 0.15);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        color: #60a5fa;
        flex-shrink: 0;
    }}
    .feature-name {{
        font-weight: 600;
        font-size: 0.88rem;
        color: #ffffff;
    }}
    .feature-desc {{
        font-size: 0.72rem;
        color: var(--text-sub);
    }}

    /* Footer: Exactly matches DeviceValue AI Footer */
    .footer-container {{
        border-top: 1px solid var(--border-subtle);
        margin-top: 4rem;
        padding-top: 2rem;
        padding-bottom: 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }}
    @media (min-width: 768px) {{
        .footer-container {{ flex-direction: row; }}
    }}
    .footer-left {{
        display: flex;
        align-items: center;
        gap: 0.6rem;
        color: var(--text-muted);
        font-size: 0.85rem;
    }}
    .footer-left span b {{
        color: #ffffff;
        font-weight: 600;
    }}
    .footer-right {{
        font-size: 0.75rem;
        color: var(--text-sub);
    }}
</style>

<!-- Top Navigation Bar -->
<div class="nav-bar-container">
    <div class="nav-brand">
        <div class="nav-logo-badge">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
        </div>
        <span class="nav-title">DeviceValue <span class="nav-title-accent">AI</span> <span class="nav-tag">Smartphones</span></span>
    </div>
    <div class="nav-links">
        <label for="drawer-toggle" class="nav-link-btn">Specs & Intelligence</label>
        <a href="http://localhost:5173" class="nav-cta-pill" target="_self">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
            Laptop Valuation
        </a>
    </div>
</div>

<!-- Side Drawer Toggle -->
<div id="drawer-container">
    <input type="checkbox" id="drawer-toggle">
    <label class="drawer-btn" for="drawer-toggle" title="Platform Features">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
    </label>
    <label class="drawer-overlay" for="drawer-toggle"></label>
    <div class="drawer-panel">
        <div>
            <h3 class="drawer-title">Platform Intelligence</h3>
            <p class="drawer-sub">DeviceValue AI Smartphone Core</p>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 20H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v4.5"/><path d="M16 11l5 5-5 5"/><path d="M11 16h10"/></svg></div>
            <div>
                <div class="feature-name">ML Price Prediction</div>
                <div class="feature-desc">Random Forest Regressor Engine</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg></div>
            <div>
                <div class="feature-name">5,000+ Records</div>
                <div class="feature-desc">Deep Indian Market Insights</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg></div>
            <div>
                <div class="feature-name">Multi-Brand Coverage</div>
                <div class="feature-desc">Apple, Samsung, Google & More</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg></div>
            <div>
                <div class="feature-name">Live Image Retrieval</div>
                <div class="feature-desc">Automated Web Image Sourcing</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg></div>
            <div>
                <div class="feature-name">Instant Estimates</div>
                <div class="feature-desc">Real-time local prediction</div>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="6" width="18" height="12" rx="2" ry="2"></rect><line x1="23" y1="13" x2="23" y2="11"></line><line x1="5" y1="10" x2="5" y2="14"></line><line x1="9" y1="10" x2="9" y2="14"></line></svg></div>
            <div>
                <div class="feature-name">Hardware Analytics</div>
                <div class="feature-desc">Battery Health & Condition Weighting</div>
            </div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ── Utilities & API Handlers (Functional Code Preserved Exactly) ───────────────
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
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
    """Fetch product image URL via Serper.dev / DuckDuckGo / Glassmorphic SVG."""
    brand_str = str(brand).strip()
    model_str = str(model).strip()
    cache_key = f"{brand_str}|{model_str}".lower()

    if brand_str.lower() == "apple" and model_str.lower() == "iphone 12 pro":
        return "https://pngimg.com/uploads/iphone_12/iphone_12_PNG20.png"

    if cache_key in _image_cache:
        return _image_cache[cache_key]

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
                    for img in images:
                        cand = img.get("imageUrl", "")
                        if cand and _is_trusted_url(cand):
                            img_url = cand
                            break
                    if not img_url:
                        for img in images:
                            cand = img.get("imageUrl", "")
                            if cand and not any(w in cand.lower() for w in ["mockup", "template", "dummy"]):
                                img_url = cand
                                break
                    if not img_url:
                        img_url = images[0].get("imageUrl", "")
                    if img_url:
                        _image_cache[cache_key] = img_url
                        return img_url
        except Exception:
            pass

    if DDGS is not None:
        try:
            ddg_query = f"{brand_str} {model_str} smartphone official product image white background"
            with DDGS() as ddgs:
                results = ddgs.images(ddg_query, max_results=10, safesearch="strict")
                if results:
                    img_url = ""
                    for r in results:
                        cand = r.get("image", "")
                        if cand and _is_trusted_url(cand):
                            img_url = cand
                            break
                    if not img_url:
                        for r in results:
                            cand = r.get("image", "")
                            if cand and not any(w in cand.lower() for w in ["mockup", "template", "dummy"]):
                                img_url = cand
                                break
                    if not img_url:
                        img_url = results[0].get("image", "")
                    if img_url:
                        _image_cache[cache_key] = img_url
                        return img_url
        except Exception:
            pass

    svg = _generate_svg_placeholder(brand_str, model_str)
    _image_cache[cache_key] = svg
    return svg


def _generate_svg_placeholder(brand: str, model: str) -> str:
    """Generate DeviceValue AI style SVG placeholder showing Brand + Model."""
    safe_brand = brand.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    safe_model = model.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 480" width="400" height="480">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e1a"/>
      <stop offset="50%" stop-color="#0f1629"/>
      <stop offset="100%" stop-color="#151d35"/>
    </linearGradient>
    <linearGradient id="border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="rgba(59,130,246,0.6)"/>
      <stop offset="50%" stop-color="rgba(139,92,246,0.3)"/>
      <stop offset="100%" stop-color="rgba(59,130,246,0.5)"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#60a5fa"/>
      <stop offset="100%" stop-color="#a78bfa"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <rect width="400" height="480" rx="20" fill="url(#bg)"/>
  <rect width="400" height="480" rx="20" fill="none" stroke="url(#border)" stroke-width="1.5"/>
  <circle cx="200" cy="200" r="140" fill="rgba(59,130,246,0.08)"/>
  <rect x="135" y="70" width="130" height="250" rx="20" fill="none" stroke="rgba(59,130,246,0.35)" stroke-width="1.5" filter="url(#glow)"/>
  <rect x="135" y="70" width="130" height="250" rx="20" fill="rgba(15,22,41,0.6)"/>
  <circle cx="200" cy="92" r="5" fill="none" stroke="rgba(59,130,246,0.4)" stroke-width="1"/>
  <rect x="145" y="110" width="110" height="180" rx="6" fill="rgba(59,130,246,0.04)" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
  <text x="200" y="375" text-anchor="middle" font-family="'Instrument Sans', sans-serif" font-weight="700" font-size="22" fill="url(#accent)">{safe_brand}</text>
  <text x="200" y="405" text-anchor="middle" font-family="'DM Sans', sans-serif" font-weight="400" font-size="15" fill="#94a3b8">{safe_model}</text>
  <text x="200" y="445" text-anchor="middle" font-family="'DM Sans', sans-serif" font-weight="500" font-size="10" fill="rgba(148,163,184,0.4)" letter-spacing="2">SMARTPHONE VISUAL</text>
</svg>'''

    encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{encoded}"


def render_phone_visual(brand: str, model: str) -> str:
    """Render the phone image card with clean DeviceValue AI styling."""
    img_src = fetch_phone_image(brand, model)
    is_svg = img_src.startswith("data:")
    img_style = "width:100%; max-height:260px; object-fit:contain; border-radius:12px;"
    onerror = "" if is_svg else " onerror=\"this.src='';this.style.display='none'\""
    return (
        f'<div class="phone-visual-card">'
        f'<img src="{img_src}" style="{img_style}" alt="{brand} {model}"{onerror}>'
        f'</div>'
    )


def create_styled_chart(months, prices):
    """Create a clean, refined Plotly chart matching DeviceValue AI."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=months,
            y=prices,
            mode="lines+markers",
            line=dict(color="#3b82f6", width=3.5, shape="spline"),
            marker=dict(size=8, color="#0f1629", line=dict(width=2, color="#3b82f6")),
            hoverinfo="text",
            text=[f"Month {m}: ₹ {p:,.0f}" for m, p in zip(months, prices)],
            name="Value Forecast",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=months,
            y=prices,
            mode="lines",
            line=dict(color="rgba(59, 130, 246, 0.2)", width=8, shape="spline"),
            hoverinfo="skip",
        )
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=15, b=0),
        showlegend=False,
        height=280,
        xaxis=dict(
            showgrid=True,
            gridcolor="#1c2744",
            tickfont=dict(color="#94a3b8", family="DM Sans", size=11),
            title=dict(text="Holding Period (Months)", font=dict(color="#64748b", size=12, family="DM Sans")),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1c2744",
            tickfont=dict(color="#94a3b8", family="DM Sans", size=11),
            tickprefix="₹ ",
            title=dict(text="Estimated Value", font=dict(color="#64748b", size=12, family="DM Sans")),
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#151d35", bordercolor="rgba(255,255,255,0.1)", font_size=12, font_family="DM Sans", font_color="#f1f5f9"),
    )
    return fig


# ── Load Artifacts & Datasets (Preserved Exactly) ──────────────────────────────
try:
    model_obj, encoders = load_artifacts()
    data_path = os.path.join(os.path.dirname(__file__), "data", "used_phones_clean.csv")
    df_raw = pd.read_csv(data_path)
    variants_path = os.path.join(
        os.path.dirname(__file__), "data", "phone_variants.csv"
    )
    variants_df = pd.read_csv(variants_path)
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
    model_price_map = df_raw.groupby("model")["launch_price"].median().to_dict()
    conditions = sorted(
        get_known_conditions(encoders),
        key=lambda x: ["Excellent", "Good", "Fair", "Poor"].index(x),
    )
except Exception as e:
    st.error(f"System Error: {e}")
    st.stop()


# ── Hero Section (DeviceValue AI Architecture) ────────────────────────────────
st.markdown(
    f"""
<div class="hero-container">
    <div class="hero-card">
        <div class="hero-content">
            <div class="hero-badge">
                <span class="hero-badge-dot"></span>
                <span>Electronic Device Value Prediction System</span>
            </div>
            <h1 class="hero-title">
                Know What Your <span class="hero-title-accent">Device</span> Is Worth.
            </h1>
            <p class="hero-subtitle">
                Estimate your smartphone's resale value using machine learning, verified Indian market trends, and hardware specifications.
            </p>
            <div class="hero-stats">
                <div class="hero-stat-pill">
                    <span class="hero-stat-val">5,000+</span>
                    <span class="hero-stat-lbl">Market Records</span>
                </div>
                <div class="hero-stat-pill">
                    <span class="hero-stat-val">50+</span>
                    <span class="hero-stat-lbl">Brands</span>
                </div>
                <div class="hero-stat-pill">
                    <span class="hero-stat-val">98%</span>
                    <span class="hero-stat-lbl">Accuracy Benchmark</span>
                </div>
            </div>
        </div>
        <div class="hero-visual-col">
            <div class="hero-halo"></div>
            <img src="data:image/png;base64,{iphone_b64}" class="iphone-overlay-card" alt="iPhone">
            <img src="data:image/png;base64,{samsung_b64}" class="samsung-overlay-card" alt="Samsung">
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


def mobile_selector(label, options, key):
    """Custom Searchable Popover selector styled to match DeviceValue AI."""
    if key not in st.session_state or st.session_state[key] is None:
        st.session_state[key] = options[0] if options else ""

    selected = str(st.session_state[key] or "")

    st.markdown(
        f'<p class="custom-field-label">{label}</p>',
        unsafe_allow_html=True,
    )

    with st.popover(selected, use_container_width=True):
        search_enabled = st.toggle("🔍 Filter options", key=f"{key}_search_toggle")

        if search_enabled:
            query = st.text_input("Search...", key=f"{key}_search_input")
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


# ── Main Two-Column Layout ────────────────────────────────────────────────────
main_col1, main_col2 = st.columns([1, 1.15], gap="large")

with main_col1:
    st.markdown('<div id="analyze-section"></div>', unsafe_allow_html=True)
    
    brand = mobile_selector("Select Brand", brands, "selected_brand")
    brand = str(brand or "")

    brand_models = sorted(brand_model_map.get(brand, []))

    if st.session_state.get("last_brand") != brand:
        st.session_state["selected_model"] = brand_models[0] if brand_models else ""
        st.session_state["last_brand"] = brand

    with st.container():
        st.subheader("Device Hardware Specifications")

        model_name = mobile_selector("Model Variant", brand_models, "selected_model")
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

            ram = st.selectbox("RAM Capacity (GB)", options=ram_options)

            storage_options = (
                sorted(model_variants[model_variants["ram"] == ram]["rom"].unique())
                if not model_variants.empty
                else [32, 64, 128, 256, 512]
            )

            storage = st.selectbox("Storage Capacity (GB)", options=storage_options)

        with c2:
            age_months = st.slider("Device Age (Months)", 1, 60, 12)
            battery = st.slider("Battery Health (%)", 50, 100, 90)

        condition = st.selectbox("Physical & Functional Condition", options=conditions)

    predict_clicked = st.button(
        "ANALYZE MARKET VALUE", type="primary", use_container_width=True
    )


with main_col2:
    # ── Resolve selected smartphone data & database variants dynamically ──────
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
        launch_price = float(variant_price) if pd.notna(variant_price) else float(model_price_map.get(model_name, 25000))
    else:
        launch_price = float(model_price_map.get(model_name, 25000))

    if not model_variants.empty:
        distinct_configs = (
            model_variants.drop_duplicates(subset=["ram", "rom"])
            .sort_values(by=["ram", "rom"])
        )
        configs_list = [f"{int(r['ram'])}GB+{int(r['rom'])}GB" for _, r in distinct_configs.iterrows()]
        variants_summary = " • ".join(configs_list)
    else:
        variants_summary = f"{ram}GB+{storage}GB"

    # Display Polished Product-Information Card (Updates dynamically on any selection change)
    st.markdown(
        f"""
<div class="product-info-card card-glow">
    <div class="product-header">
        <div class="product-header-badge">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
            <span>Verified Device Profile</span>
        </div>
        <h3 class="product-title">{brand} {model_name}</h3>
        <p class="product-sub">Real-time smartphone hardware configuration from project dataset</p>
    </div>
    <div class="spec-table">
        <div class="spec-row">
            <span class="spec-label">Brand & Model</span>
            <span class="spec-value">{brand} {model_name}</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Active Hardware Configuration</span>
            <span class="spec-value spec-value-accent">{ram} GB RAM · {storage} GB Storage</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Device Age</span>
            <span class="spec-value">{age_months} Months ({age_months / 12:.1f} Yrs)</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Battery Health</span>
            <span class="spec-value">{battery}% Capacity</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Cosmetic Condition</span>
            <span class="spec-value">{condition}</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Launch Price Benchmark</span>
            <span class="spec-value">₹ {launch_price:,.0f}</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Available Model Variants</span>
            <span class="spec-value text-slate-300" style="font-size: 0.82rem; text-align: right; max-width: 60%;">{variants_summary}</span>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    if predict_clicked:
        spinner_messages = [
            "Connecting to market intelligence...",
            "Evaluating hardware specifications...",
            "Applying condition & battery weightings...",
            "Computing resale market value...",
        ]
        with st.spinner(random.choice(spinner_messages)):
            # Functional Prediction Call (Preserved 100%)
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
            retention_pct = (price / launch_price * 100) if launch_price > 0 else 0

            # Result Card matching DeviceValue AI PredictionResult.jsx
            st.markdown(
                f"""
<div class="result-card">
    <div class="result-badge">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        <span>Verified Market Valuation</span>
    </div>
    <div class="result-label">Estimated Current Value</div>
    <div class="result-price">₹ {price:,.0f}</div>
    <div class="result-subtext">Estimated based on ML trained secondary market intelligence.</div>
    <div class="spec-table">
        <div class="spec-row">
            <span class="spec-label">Original Launch Price</span>
            <span class="spec-value">₹ {launch_price:,.0f}</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Value Retention</span>
            <span class="spec-value spec-value-accent">{retention_pct:.1f}%</span>
        </div>
        <div class="spec-row">
            <span class="spec-label">Fair Resale Range</span>
            <span class="spec-value">₹ {low:,.0f} – ₹ {high:,.0f}</span>
        </div>
    </div>
</div>
""",
                unsafe_allow_html=True,
            )

            res1, res2 = st.columns([1, 1.7])
            with res1:
                st.markdown(
                    render_phone_visual(brand, model_name),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='text-align:center; color:#94a3b8; font-size:0.8rem; margin-top:-0.5rem;'>{brand} {model_name}</p>",
                    unsafe_allow_html=True,
                )

            with res2:
                with st.container():
                    st.subheader("Resale Lifecycle Forecast")
                    months_f = list(range(age_months, age_months + 25, 4))
                    future_prices = [
                        price * (0.96 ** (m - age_months)) for m in months_f
                    ]

                    fig = create_styled_chart(months_f, future_prices)
                    st.plotly_chart(
                        fig, use_container_width=True, config={"displayModeBar": False}
                    )
                    st.caption("Forecasted depreciation trajectory over the next 24 months")
    else:
        st.markdown(
            """
<div class="idle-card">
    <div class="idle-icon-badge">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>
    </div>
    <div class="idle-title">Ready for Valuation</div>
    <p class="idle-sub">Hardware configuration verified above. Click <b>ANALYZE MARKET VALUE</b> to compute the real-time secondary market prediction.</p>
</div>
""",
            unsafe_allow_html=True,
        )


# ── Footer: Styled identically to DeviceValue AI Footer ───────────────────────
st.markdown(
    """
<div class="footer-container">
    <div class="footer-left">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/></svg>
        <span><b>DeviceValue AI</b> — Electronic Device Value Prediction System (Smartphone Edition)</span>
    </div>
    <div class="footer-right">
        Academic project · Data Science &amp; Machine Learning · Navrachana University
    </div>
</div>
""",
    unsafe_allow_html=True,
)
