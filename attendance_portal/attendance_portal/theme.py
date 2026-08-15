"""
Shared visual theme for the Attendance Portal: a 'verification terminal'
aesthetic grounded in what this app actually does (biometric checkpoint
verification), rather than a generic dashboard reskin.

Palette:
  ink      #10151C  page background (graphite-navy, not pure black)
  panel    #1A222C  card/sidebar background
  panel-2  #212B37  raised elements (metrics, buttons, inputs)
  paper    #F7F5F0  used sparingly for high-contrast stamp elements
  scan     #2BB3A3  'verified' signal (teal)
  reject   #E2543A  'rejected' signal (warm red-orange)
  badge    #E8B94A  secondary accent (ID/badge highlights)

Type: JetBrains Mono for anything technical (headers, IDs, confidence
numbers, data tables) paired with Inter for body/prose text.

Import and call inject_theme() once near the top of every page, right
after st.set_page_config().
"""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

:root {
    --ink: #10151C;
    --panel: #1A222C;
    --panel-2: #212B37;
    --paper: #F7F5F0;
    --scan: #2BB3A3;
    --scan-dim: rgba(43,179,163,0.15);
    --reject: #E2543A;
    --reject-dim: rgba(226,84,58,0.15);
    --badge: #E8B94A;
    --text: #E7EAEE;
    --text-muted: #8B96A3;
    --hairline: rgba(255,255,255,0.09);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: var(--ink); color: var(--text); }

h1, h2, h3 {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em;
    color: var(--text) !important;
}
p, span, label, div { color: var(--text); }
.stCaption, [data-testid="stCaptionContainer"] { color: var(--text-muted) !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: var(--panel); border-right: 1px solid var(--hairline); }
[data-testid="stSidebarNav"] a {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--text-muted) !important;
    border-radius: 6px;
}
[data-testid="stSidebarNav"] a:hover { color: var(--scan) !important; background: var(--scan-dim); }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: var(--scan) !important;
    background: var(--scan-dim);
    border-left: 2px solid var(--scan);
}

/* Hide default Streamlit chrome for a cleaner, less templated feel */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { visibility: hidden; }

/* Buttons */
.stButton > button {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.02em;
    border-radius: 6px;
    border: 1px solid var(--hairline);
    background: var(--panel-2);
    color: var(--text);
    transition: all 0.15s ease;
}
.stButton > button:hover { border-color: var(--scan); color: var(--scan); }
.stButton > button[kind="primary"] { background: var(--scan); color: var(--ink); border: none; }
.stButton > button[kind="primary"]:hover { background: #26a394; color: var(--ink); }

/* Metrics */
[data-testid="stMetric"] {
    background: var(--panel-2);
    border: 1px solid var(--hairline);
    border-radius: 8px;
    padding: 16px 18px;
}
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; color: var(--scan) !important; }
[data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-muted) !important;
    font-size: 12px !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* Bordered containers (used for hero nav cards) */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--panel-2);
    border: 1px solid var(--hairline) !important;
    border-radius: 10px;
}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"] > div {
    background: var(--panel-2) !important;
    border: 1px solid var(--hairline) !important;
    color: var(--text) !important;
    border-radius: 6px;
}
.stSlider [data-baseweb="slider"] { color: var(--scan); }

/* Dataframes -- technical readout feel */
[data-testid="stDataFrame"] { font-family: 'JetBrains Mono', monospace; }

/* Alerts */
div[data-testid="stAlert"] { border-radius: 8px; font-family: 'Inter', sans-serif; }

/* --- Terminal header component --- */
.term-header { margin-bottom: 1.5rem; }
.term-header-top { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.term-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--scan);
    box-shadow: 0 0 6px var(--scan);
    display: inline-block;
}
.status-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--scan);
    letter-spacing: 0.04em;
}
.term-title { font-size: 26px !important; margin: 0 0 4px 0 !important; }
.term-subtitle { font-family: 'Inter', sans-serif; font-size: 14px; color: var(--text-muted); margin: 0; }

/* --- Verification readout (signature component) --- */
.readout {
    background: var(--panel-2);
    border: 1px solid var(--hairline);
    border-left: 3px solid;
    border-radius: 10px;
    padding: 20px 24px;
    margin: 12px 0 20px 0;
    position: relative;
}
.readout-stamp {
    position: absolute;
    top: 18px; right: 22px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.12em;
    border: 1.5px solid;
    border-radius: 4px;
    padding: 3px 10px;
    transform: rotate(3deg);
}
.readout-name {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: var(--text-muted);
    margin-bottom: 2px;
}
.readout-confidence {
    font-family: 'JetBrains Mono', monospace;
    font-size: 42px;
    font-weight: 700;
    line-height: 1.1;
}
.readout-pct-sign { font-size: 22px; opacity: 0.7; }
.readout-bar-track {
    position: relative;
    height: 8px;
    background: var(--ink);
    border-radius: 4px;
    margin-top: 14px;
    overflow: visible;
}
.readout-bar-fill { position: absolute; left: 0; top: 0; height: 100%; border-radius: 4px; transition: width 0.4s ease; }
.readout-threshold {
    position: absolute;
    top: -3px;
    width: 2px;
    height: 14px;
    background: var(--text-muted);
}
.readout-caption {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 8px;
    letter-spacing: 0.02em;
}

/* --- Eigenface grid tiles --- */
.eigentile { border: 1px solid var(--hairline); border-radius: 6px; overflow: hidden; background: var(--panel-2); }
.eigentile-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    text-align: center;
    padding: 4px 0;
    letter-spacing: 0.04em;
}
</style>
"""


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)


def render_header(title, subtitle, status_text=None):
    status_html = (
        f'<span class="status-dot"></span><span class="status-text">{status_text}</span>'
        if status_text else ""
    )
    st.markdown(
        f"""
        <div class="term-header">
            <div class="term-header-top">
                <span class="term-tag">ATTENDANCE VERIFICATION SYSTEM</span>
                {status_html}
            </div>
            <h1 class="term-title">{title}</h1>
            <p class="term-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_verification_readout(accepted, name, confidence, threshold=0.6):
    """
    The signature UI moment: a terminal-style readout for a login attempt,
    with a stamped VERIFIED/REJECTED badge and a threshold bar instead of
    a plain st.success/st.error message.
    """
    color = "var(--scan)" if accepted else "var(--reject)"
    stamp = "VERIFIED" if accepted else "REJECTED"
    pct = max(0.0, min(confidence * 100, 100.0))
    threshold_pct = max(0.0, min(threshold * 100, 100.0))
    st.markdown(
        f"""
        <div class="readout" style="border-left-color:{color};">
            <div class="readout-stamp" style="color:{color}; border-color:{color};">{stamp}</div>
            <div class="readout-name">{name}</div>
            <div class="readout-confidence" style="color:{color};">{pct:.1f}<span class="readout-pct-sign">%</span></div>
            <div class="readout-bar-track">
                <div class="readout-bar-fill" style="width:{pct}%; background:{color};"></div>
                <div class="readout-threshold" style="left:{threshold_pct}%;"></div>
            </div>
            <div class="readout-caption">confidence vs. {threshold_pct:.0f}% accept threshold</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
