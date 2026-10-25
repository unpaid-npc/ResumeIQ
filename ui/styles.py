"""Dark theme for ResumeIQ: color palette and custom CSS for Streamlit."""

import streamlit as st

# Single source of truth for colors. Other files import this dict.
COLORS = {
    "bg": "#0B0F14",
    "sidebar": "#111720",
    "card": "#151C26",
    "border": "#243042",
    "primary": "#7C5CFC",
    "secondary": "#38BDF8",
    "text": "#F3F4F6",
    "muted": "#9CA3AF",
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
}


def _css_variables() -> str:
    """Turn the COLORS dict into CSS custom properties (e.g. --riq-card)."""
    lines = [f"  --riq-{name}: {value};" for name, value in COLORS.items()]
    return ":root {\n" + "\n".join(lines) + "\n}\n"


_BASE_CSS = """
/* ---------- Page background and text ---------- */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color: var(--riq-bg) !important;
  color: var(--riq-text);
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 1100px; }

h1, h2, h3, h4 { color: var(--riq-text) !important; letter-spacing: -0.01em; }
p, li, label, span { color: var(--riq-text); }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background-color: var(--riq-sidebar) !important;
  border-right: 1px solid var(--riq-border);
}
[data-testid="stSidebar"] .stRadio label {
  padding: 0.55rem 0.8rem;
  border-radius: 10px;
  transition: background 0.15s ease;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(124, 92, 252, 0.12);
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
  background: linear-gradient(135deg, rgba(124,92,252,0.22), rgba(56,189,248,0.10));
  border: 1px solid var(--riq-border);
  border-radius: 20px;
  padding: 2rem 2.2rem;
  margin-bottom: 1.2rem;
}
.riq-hero h1 { margin: 0 0 0.4rem 0; font-size: 2.1rem; }
.riq-hero p { color: var(--riq-muted); font-size: 1.05rem; margin: 0; }

/* ---------- Brand and badges ---------- */
.riq-brand { font-size: 1.5rem; font-weight: 700; color: var(--riq-text); }
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
.riq-badge-success { color: var(--riq-success); background: rgba(52,211,153,0.10); }
.riq-badge-warning { color: var(--riq-warning); background: rgba(251,191,36,0.10); }
.riq-badge-error   { color: var(--riq-error);   background: rgba(248,113,113,0.10); }
.riq-badge-info    { color: var(--riq-secondary); background: rgba(56,189,248,0.10); }

.riq-card .riq-badge { margin-top: 0.9rem; }

.riq-agent-num {
  display: inline-flex; align-items: center; justify-content: center;
  width: 1.8rem; height: 1.8rem; margin-bottom: 0.7rem;
  border-radius: 8px; font-weight: 700;
  background: rgba(124, 92, 252, 0.2); color: var(--riq-primary);
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
.riq-step-active { color: var(--riq-secondary); font-weight: 600; }
.riq-step-failed { color: var(--riq-error); font-weight: 600; }

/* ---------- Buttons ---------- */
.stButton > button, .stDownloadButton > button {
  background: var(--riq-primary);
  color: #FFFFFF;
  border: none;
  border-radius: 10px;
  padding: 0.6rem 1.4rem;
  font-weight: 600;
  transition: filter 0.15s ease, transform 0.05s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  filter: brightness(1.15);
  color: #FFFFFF;
}
.stButton > button:active { transform: scale(0.98); }
.stButton > button:disabled {
  background: var(--riq-border); color: var(--riq-muted);
}

/* ---------- Inputs and uploader ---------- */
textarea, input {
  background-color: var(--riq-card) !important;
  color: var(--riq-text) !important;
  border: 1px solid var(--riq-border) !important;
  border-radius: 10px !important;
}
textarea:focus, input:focus { border-color: var(--riq-primary) !important; }
[data-testid="stFileUploaderDropzone"] {
  background-color: var(--riq-card);
  border: 1px dashed var(--riq-primary);
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
    return "<style>\n" + _css_variables() + _BASE_CSS + "\n</style>"


def inject_styles() -> None:
    """Apply the dark theme to the current Streamlit page. Call once per run."""
    st.markdown(build_css(), unsafe_allow_html=True)