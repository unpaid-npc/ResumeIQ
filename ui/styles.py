"""Dark theme for ResumeIQ: color palette and custom CSS for Streamlit.

Look: neutral dark grays with soft Google-style accents. The font is DM Sans
(a free font close to Google Sans, which is not freely available).
"""

import streamlit as st

# Single source of truth for colors. Other files import this dict.
COLORS = {
    "bg": "#161616",
    "sidebar": "#1C1C1C",
    "card": "#202020",
    "border": "#333333",
    "primary": "#8AB4F8",
    "secondary": "#669DF6",
    "text": "#E8EAED",
    "muted": "#9AA0A6",
    "success": "#81C995",
    "warning": "#FDD663",
    "error": "#F28B82",
}

# Loaded by the browser from Google Fonts. If it fails, the fallbacks are used.
FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=DM+Sans:wght@400;500;600;700&display=swap');\n"
)
FONT_STACK = "'Google Sans', 'Google Sans Text', 'DM Sans', 'Segoe UI', Arial, sans-serif"


def _css_variables() -> str:
    """Turn the COLORS dict into CSS custom properties (e.g. --riq-card)."""
    lines = [f"  --riq-{name}: {value};" for name, value in COLORS.items()]
    lines.append(f"  --riq-font: {FONT_STACK};")
    return ":root {\n" + "\n".join(lines) + "\n}\n"


_BASE_CSS = """
/* ---------- Fonts (icons are left alone) ---------- */
html, body, .stApp, p, h1, h2, h3, h4, label, li, button, input, textarea,
[data-testid="stMarkdownContainer"], [data-testid="stCaptionContainer"] {
  font-family: var(--riq-font);
}

/* ---------- Page background and text ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color: var(--riq-bg) !important;
  color: var(--riq-text);
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }

h1, h2, h3, h4 { color: var(--riq-text) !important; letter-spacing: -0.01em; font-weight: 500; }
p, li, label, span { color: var(--riq-text); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background-color: var(--riq-sidebar) !important;
  border-right: 1px solid var(--riq-border);
}
[data-testid="stSidebar"] .stRadio label {
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  transition: background 0.15s ease;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255, 255, 255, 0.06); }
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
  background: rgba(138, 180, 248, 0.16);
}

/* ---------- Cards ---------- */
.riq-card {
  background: var(--riq-card);
  border: 1px solid var(--riq-border);
  border-radius: 16px;
  padding: 1.4rem 1.5rem;
  margin-bottom: 1rem;
}
.riq-card h3 { margin-top: 0; font-size: 1.1rem; }
.riq-card p { color: var(--riq-muted); margin-bottom: 0; line-height: 1.55; }
.riq-hero {
  background: linear-gradient(135deg, rgba(138,180,248,0.14), rgba(255,255,255,0.02));
  border: 1px solid var(--riq-border);
  border-radius: 20px;
  padding: 2rem 2.2rem;
  margin-bottom: 1.2rem;
}
.riq-hero h1 { margin: 0 0 0.4rem 0; font-size: 2.1rem; }
.riq-hero p { color: var(--riq-muted); font-size: 1.05rem; margin: 0; }

/* ---------- Brand and badges ---------- */
.riq-brand { font-size: 1.5rem; font-weight: 600; color: var(--riq-text); }
.riq-brand span { color: var(--riq-primary); }
.riq-tagline { color: var(--riq-muted); font-size: 0.85rem; margin-bottom: 1rem; }
.riq-badge {
  display: inline-block;
  padding: 0.15rem 0.7rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid currentColor;
}
.riq-badge-success { color: var(--riq-success); background: rgba(129,201,149,0.10); }
.riq-badge-warning { color: var(--riq-warning); background: rgba(253,214,99,0.10); }
.riq-badge-error   { color: var(--riq-error);   background: rgba(242,139,130,0.10); }
.riq-badge-info    { color: var(--riq-primary); background: rgba(138,180,248,0.10); }
.riq-card .riq-badge { margin-top: 0.9rem; }

/* ---------- Agent cards and stats ---------- */
.riq-agent-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 1.8rem; height: 1.8rem; margin-bottom: 0.7rem;
  border-radius: 8px; font-weight: 700;
  background: rgba(138, 180, 248, 0.18); color: var(--riq-primary);
}
.riq-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.8rem; margin-top: 1rem; }
.riq-stat {
  padding: 0.7rem 1rem;
  background: var(--riq-bg); border: 1px solid var(--riq-border); border-radius: 12px;
}
.riq-stat b { display: block; font-size: 1.7rem; color: var(--riq-text); }
.riq-stat span { color: var(--riq-muted); font-size: 0.85rem; }

/* ---------- Progress steps ---------- */
.riq-step {
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.55rem 0.2rem; color: var(--riq-muted);
}
.riq-step-done { color: var(--riq-success); }
.riq-step-active { color: var(--riq-primary); font-weight: 600; }
.riq-step-failed { color: var(--riq-error); font-weight: 600; }

/* ---------- Buttons ---------- */
.stButton button, .stDownloadButton button,
[data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-primary"] {
  background: var(--riq-primary) !important;
  border: none !important;
  border-radius: 999px !important;
  padding: 0.6rem 1.6rem;
  font-weight: 600;
  transition: filter 0.15s ease, transform 0.05s ease;
}
.stButton button p, .stDownloadButton button p,
[data-testid="stBaseButton-secondary"] p, [data-testid="stBaseButton-primary"] p {
  color: #111111 !important;
}
.stButton button:hover, .stDownloadButton button:hover { filter: brightness(1.12); }
.stButton button:active { transform: scale(0.98); }
.stButton button:disabled, [data-testid="stBaseButton-secondary"]:disabled {
  background: var(--riq-border) !important;
}
.stButton button:disabled p, [data-testid="stBaseButton-secondary"]:disabled p {
  color: var(--riq-muted) !important;
}

/* ---------- Inputs and uploader ---------- */
textarea, input {
  background-color: var(--riq-card) !important;
  color: var(--riq-text) !important;
  border: 1px solid var(--riq-border) !important;
  border-radius: 12px !important;
}
textarea:focus, input:focus { border-color: var(--riq-primary) !important; }
[data-testid="stFileUploaderDropzone"] {
  background-color: var(--riq-card);
  border: 1px dashed var(--riq-border);
  border-radius: 14px;
}

/* ---------- Alerts and expanders ---------- */
[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stExpander"] {
  background: var(--riq-card);
  border: 1px solid var(--riq-border);
  border-radius: 12px;
}
hr { border-color: var(--riq-border) !important; }
"""


def build_css() -> str:
    """Return the complete stylesheet as one string (easy to test)."""
    return "<style>\n" + FONT_IMPORT + _css_variables() + _BASE_CSS + "\n</style>"


def inject_styles() -> None:
    """Apply the dark theme to the current Streamlit page. Call once per run."""
    st.markdown(build_css(), unsafe_allow_html=True)