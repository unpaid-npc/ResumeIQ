"""ResumeIQ - Streamlit entry point.

Run with:  streamlit run app.py
"""

import streamlit as st

from ui.components import render_sidebar_brand
from ui.pages import PAGES
from ui.styles import inject_styles

# set_page_config must be the first Streamlit call.
st.set_page_config(page_title="ResumeIQ", page_icon="◆", layout="wide")
inject_styles()

render_sidebar_brand()
choice = st.sidebar.radio("Navigation", list(PAGES), label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption(
    "Privacy: uploaded resumes are read from a temporary file and are never "
    "saved in the project folder."
)

PAGES[choice]()