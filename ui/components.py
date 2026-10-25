"""Reusable dark-theme UI pieces for ResumeIQ.

Every function that takes text escapes it first, so resume content or model
output can never inject HTML into the page.
"""

from html import escape

import streamlit as st

# Allowed badge kinds. Anything else falls back to "info".
BADGE_KINDS = ("success", "warning", "error", "info")

# Progress step states and the icon shown for each.
STEP_ICONS = {
    "pending": "○",
    "active": "◉",
    "done": "✔",
    "failed": "✖",
}


def badge_html(text: str, kind: str = "info") -> str:
    """Return the HTML for a small colored status badge."""
    if kind not in BADGE_KINDS:
        kind = "info"
    return f'<span class="riq-badge riq-badge-{kind}">{escape(text)}</span>'


def hero_html(title: str, subtitle: str) -> str:
    """Return the HTML for the large banner at the top of a page."""
    return (
        '<div class="riq-hero">'
        f"<h1>{escape(title)}</h1>"
        f"<p>{escape(subtitle)}</p>"
        "</div>"
    )


def card_html(title: str, body: str, badge: str = "") -> str:
    """Return the HTML for a card. `badge` is already-built badge HTML or ''."""
    return (
        '<div class="riq-card">'
        f"<h3>{escape(title)}</h3>"
        f"<p>{escape(body)}</p>"
        f"{badge}"
        "</div>"
    )


def steps_html(steps: list[tuple[str, str]]) -> str:
    """Return HTML for a progress list.

    `steps` is a list of (label, state) pairs, where state is one of
    "pending", "active", "done" or "failed".
    """
    rows = []
    for label, state in steps:
        if state not in STEP_ICONS:
            state = "pending"
        icon = STEP_ICONS[state]
        rows.append(
            f'<div class="riq-step riq-step-{state}">'
            f"<span>{icon}</span><span>{escape(label)}</span></div>"
        )
    return '<div class="riq-card">' + "".join(rows) + "</div>"


def render_sidebar_brand() -> None:
    """Draw the ResumeIQ logo text and tagline at the top of the sidebar."""
    st.sidebar.markdown(
        '<div class="riq-brand">Resume<span>IQ</span></div>'
        '<div class="riq-tagline">AI-powered resume review</div>',
        unsafe_allow_html=True,
    )


def render_hero(title: str, subtitle: str) -> None:
    """Draw a page banner."""
    st.markdown(hero_html(title, subtitle), unsafe_allow_html=True)


def render_card(title: str, body: str, badge: str = "") -> None:
    """Draw one card."""
    st.markdown(card_html(title, body, badge), unsafe_allow_html=True)


def render_steps(steps: list[tuple[str, str]], placeholder=None) -> None:
    """Draw the progress list. Pass a Streamlit placeholder to update in place."""
    target = placeholder if placeholder is not None else st
    target.markdown(steps_html(steps), unsafe_allow_html=True)