"""The two ResumeIQ pages: Dashboard and Analyze Resume."""

import os
from html import escape

import streamlit as st
from dotenv import load_dotenv

from backend.schemas import FinalReport
from ui.components import (
    badge_html,
    card_html,
    render_card,
    render_hero,
    render_steps,
)
from ui.runner import STEP_KEYS, STEP_LABELS, InputError, analyze_upload
from ui.validation import describe_error, validate_job_description

REQUIRED_SETTINGS = ("LLM_PROVIDER", "LLM_API_KEY", "LLM_MODEL")

# (name, description, optional?) for the agent team shown on the Dashboard.
AGENTS = (
    ("Resume Parser", "Turns the raw resume text into structured data.", False),
    (
        "Skills Analyst",
        "Finds the skills you list and looks for evidence of them in your experience.",
        False,
    ),
    (
        "Resume Evaluator",
        "Scores the resume quality and identifies strengths and weaknesses.",
        False,
    ),
    (
        "Job Matcher",
        "Compares the resume with a job description. Runs only when you provide one.",
        True,
    ),
    (
        "Feedback Writer",
        "Writes the summary, recommendations and bullet rewrites. It writes words "
        "only: skills, scores and job match are copied by our code, not by the AI.",
        False,
    ),
)


def _clean(text: str) -> str:
    """Collapse all whitespace (including blank lines) into single spaces."""
    return " ".join(str(text).split())


def _list_card_html(title: str, items: list[str]) -> str:
    """Build a card containing a bullet list. Every item is escaped."""
    if items:
        rows = "".join(f"<li>{escape(_clean(item))}</li>" for item in items)
        body = f"<ul>{rows}</ul>"
    else:
        body = "<p>Nothing to show.</p>"
    return f'<div class="riq-card"><h3>{escape(title)}</h3>{body}</div>'


def _agent_card_html(number: int, name: str, description: str, optional: bool) -> str:
    """Build one agent card with its step number."""
    badge = badge_html("Optional", "info") if optional else ""
    return (
        '<div class="riq-card">'
        f'<div class="riq-agent-num">{number}</div>'
        f"<h3>{escape(name)}</h3>"
        f"<p>{escape(description)}</p>"
        f"{badge}"
        "</div>"
    )


def _snapshot_html(report: FinalReport) -> str:
    """Build the 'latest analysis' panel from real counts in the report."""
    stats = (
        ("Strengths", len(report.strengths)),
        ("Weaknesses", len(report.weaknesses)),
        ("Recommendations", len(report.recommendations)),
        ("Next steps", len(report.next_steps)),
    )
    boxes = "".join(
        f'<div class="riq-stat"><b>{count}</b><span>{escape(label)}</span></div>'
        for label, count in stats
    )
    if report.job_match is not None:
        badge = badge_html("Job match included", "info")
    else:
        badge = badge_html("No job description used", "warning")
    return (
        '<div class="riq-card"><h3>Latest analysis (this session)</h3>'
        f'<p>Counts from your most recent run. Open "Analyze Resume" to read it.</p>'
        f'<div class="riq-stats">{boxes}</div>'
        f'<div style="margin-top:1rem">{badge}</div></div>'
    )


def _llm_is_configured() -> bool:
    """True when all three LLM settings have a value. Never reveals the values."""
    load_dotenv()
    return all(os.getenv(name, "").strip() for name in REQUIRED_SETTINGS)


def _error_text(exc: Exception) -> tuple[str, str]:
    """Friendly (title, detail) for any error, including rejected input."""
    if isinstance(exc, InputError):
        return "Please check your input", str(exc)
    return describe_error(exc)


# ---------------------------------------------------------------- Dashboard
def render_dashboard() -> None:
    render_hero(
        "ResumeIQ",
        "An AI resume review agent: upload a resume, optionally add a job "
        "description, and get structured, honest feedback.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        render_card(
            "1. Upload",
            "Add your resume as a PDF or DOCX file. It is read from a temporary "
            "file that is deleted straight away.",
        )
    with col2:
        render_card(
            "2. Agents analyze",
            "Several AI agents work in turn, and each output is validated before "
            "the next agent starts.",
        )
    with col3:
        render_card(
            "3. Review",
            "Read the summary, strengths, weaknesses, recommendations and next "
            "steps. Charts and bullet rewrites arrive in the next update.",
        )

    st.markdown("### Your agent team")
    for start in range(0, len(AGENTS), 3):
        cols = st.columns(3)
        for offset, (name, description, optional) in enumerate(AGENTS[start : start + 3]):
            with cols[offset]:
                st.markdown(
                    _agent_card_html(start + offset + 1, name, description, optional),
                    unsafe_allow_html=True,
                )

    left, right = st.columns(2)
    with left:
        report = st.session_state.get("report")
        if report is not None:
            st.markdown(_snapshot_html(report), unsafe_allow_html=True)
        else:
            render_card(
                "Latest analysis (this session)",
                "No analysis yet in this session. Results are not saved: they "
                "disappear when you close or reload the page.",
                badge_html("Nothing to show", "warning"),
            )
    with right:
        if _llm_is_configured():
            badge = badge_html("Settings found", "success")
            body = "The LLM settings are present in your .env file."
        else:
            badge = badge_html("Not configured", "error")
            body = (
                "One or more LLM settings are missing from your .env file "
                "(LLM_PROVIDER, LLM_API_KEY, LLM_MODEL)."
            )
        st.markdown(card_html("AI model status", body, badge), unsafe_allow_html=True)

    st.markdown(
        _list_card_html(
            "Built-in guardrails",
            [
                "Skills, scores and job match are copied by code, never rewritten by the AI.",
                "Numbers that are not in your original resume are filtered out of bullet rewrites.",
                "Each agent's output is validated before the next agent runs.",
                "A job description is optional: the app works with or without one.",
            ],
        ),
        unsafe_allow_html=True,
    )
    st.caption(
        "The model status only checks that the settings exist. It does not test "
        "the key or use any requests."
    )


# ---------------------------------------------------------- Analyze Resume
def _run_analysis(uploaded, job_text: str, steps_slot) -> None:
    """Run the analysis, redrawing the progress list as each step changes."""
    state = {key: "pending" for key in STEP_KEYS}

    def draw() -> None:
        render_steps([(STEP_LABELS[k], state[k]) for k in STEP_KEYS], steps_slot)

    def on_step(key: str, new_state: str) -> None:
        state[key] = new_state
        draw()

    st.session_state.pop("report", None)
    draw()
    try:
        report = analyze_upload(uploaded.getvalue(), uploaded.name, job_text, on_step)
    except Exception as exc:  # shown to the user in friendly form
        title, detail = _error_text(exc)
        st.error(f"**{title}**\n\n{detail}")
        return
    st.session_state["report"] = report


def _render_report(report: FinalReport) -> None:
    st.markdown("### Results")
    if report.job_match is not None:
        st.markdown(badge_html("Job match included", "info"), unsafe_allow_html=True)
    else:
        st.markdown(
            badge_html("No job description used", "warning"), unsafe_allow_html=True
        )
    st.write("")
    render_card("Executive summary", _clean(report.executive_summary))

    left, right = st.columns(2)
    with left:
        st.markdown(_list_card_html("Strengths", report.strengths), unsafe_allow_html=True)
    with right:
        st.markdown(
            _list_card_html("Weaknesses", report.weaknesses), unsafe_allow_html=True
        )
    st.markdown(
        _list_card_html("Recommendations", report.recommendations),
        unsafe_allow_html=True,
    )
    st.markdown(_list_card_html("Next steps", report.next_steps), unsafe_allow_html=True)
    st.caption(
        "Skills charts, score charts, job-match charts, bullet rewrites and "
        "downloads are coming in Day 9."
    )


def render_analyze() -> None:
    render_hero(
        "Analyze Resume",
        "Upload a PDF or DOCX resume. A job description is optional.",
    )
    st.warning(
        "Free-tier Gemini may use your inputs to improve its models. "
        "Use a synthetic resume or your own resume only."
    )

    uploaded = st.file_uploader("Resume (PDF or DOCX, max 5 MB)", type=["pdf", "docx"])
    job_text = st.text_area(
        "Job description (optional)",
        height=200,
        placeholder="Paste the full job description here, or leave this empty.",
    )

    jd_problem = validate_job_description(job_text)
    if jd_problem:
        st.warning(jd_problem)

    run = st.button(
        "Run analysis", disabled=uploaded is None or jd_problem is not None
    )
    steps_slot = st.empty()

    if run and uploaded is not None:
        _run_analysis(uploaded, job_text, steps_slot)
    elif st.session_state.get("report") is None:
        # Nothing has run yet: preview the steps so the page does not look bare.
        render_steps([(STEP_LABELS[k], "pending") for k in STEP_KEYS], steps_slot)

    report = st.session_state.get("report")
    if report is not None:
        _render_report(report)


# Label shown in the sidebar -> function that draws the page.
PAGES = {
    "Dashboard": render_dashboard,
    "Analyze Resume": render_analyze,
}