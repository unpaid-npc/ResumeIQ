"""Before/after bullet rewrites and detailed evaluation findings."""

from html import escape

import streamlit as st

from backend.schemas import BulletRewrite, Finding, ResumeEvaluation

FAITHFULNESS_NOTE = (
    "Each rewrite was checked by our code: the original line must appear in "
    "your resume, and the improved line may not add numbers your resume does "
    "not contain. Other invented claims are NOT checked automatically, so "
    "read every rewrite and only use what is true for you."
)

NO_REWRITES_NOTE = (
    "No bullet rewrites were kept for this analysis. The AI may not have "
    "produced any, or they were removed because they did not pass the "
    "faithfulness checks."
)


def _clean(text: str | None) -> str:
    """Collapse all whitespace into single spaces. None becomes ''."""
    return " ".join(str(text or "").split())


def rewrites_html(rewrites: list[BulletRewrite]) -> str:
    """One card with a before/after pair per rewrite. All text escaped."""
    items = []
    for rw in rewrites:
        note = _clean(rw.note)
        note_html = (
            f"<div style='color:var(--riq-muted);margin-top:0.4rem'>Why: {escape(note)}</div>"
            if note
            else ""
        )
        items.append(
            "<div style='margin-bottom:1.2rem'>"
            "<div style='color:var(--riq-muted);font-size:0.8rem'>BEFORE</div>"
            f"<div style='margin-bottom:0.6rem'>{escape(_clean(rw.original))}</div>"
            "<div style='color:var(--riq-success);font-size:0.8rem'>AFTER</div>"
            "<div style='border-left:3px solid var(--riq-success);padding-left:0.7rem'>"
            f"{escape(_clean(rw.improved))}</div>"
            f"{note_html}</div>"
        )
    return (
        '<div class="riq-card"><h3>Bullet rewrites</h3>'
        f"<p style='margin-bottom:1rem'>{escape(FAITHFULNESS_NOTE)}</p>"
        f"{''.join(items)}</div>"
    )


def findings_html(title: str, findings: list[Finding]) -> str:
    """Card listing findings (area, observation, evidence, suggestion)."""
    if not findings:
        return ""
    rows = []
    for f in findings:
        suggestion = _clean(f.suggestion)
        suggestion_html = (
            f"<br><span>Suggestion: {escape(suggestion)}</span>" if suggestion else ""
        )
        evidence = _clean(f.evidence)
        evidence_html = (
            f"<br><span style='color:var(--riq-muted)'>Evidence: {escape(evidence)}</span>"
            if evidence
            else ""
        )
        rows.append(
            f"<li><b>{escape(_clean(f.area))}</b>: {escape(_clean(f.observation))}"
            f"{evidence_html}{suggestion_html}</li>"
        )
    return f'<div class="riq-card"><h3>{escape(title)}</h3><ul>{"".join(rows)}</ul></div>'


def render_rewrites(rewrites: list[BulletRewrite]) -> None:
    """Draw the rewrites, or a clear message when there are none."""
    if not rewrites:
        st.info(NO_REWRITES_NOTE)
        return
    st.markdown(rewrites_html(rewrites), unsafe_allow_html=True)


def render_findings(evaluation: ResumeEvaluation | None) -> None:
    """Draw the detailed findings. Draws nothing when there is no evaluation."""
    if evaluation is None:
        return
    for title, findings in (
        ("Strengths in detail", evaluation.strengths),
        ("Areas to improve in detail", evaluation.improvements),
    ):
        html = findings_html(title, findings)
        if html:
            st.markdown(html, unsafe_allow_html=True)