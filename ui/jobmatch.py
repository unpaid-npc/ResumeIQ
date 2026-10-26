"""Job-match section: counts, a status chart, requirement details and tips."""

from html import escape

import plotly.graph_objects as go
import streamlit as st

from backend.schemas import JobMatchResult
from ui.charts import _apply_dark_layout
from ui.components import badge_html
from ui.styles import COLORS

STATUS_LABELS = {
    "supported": "Supported",
    "partial": "Partial",
    "no_evidence": "No evidence",
}
STATUS_BADGE = {"supported": "success", "partial": "warning", "no_evidence": "error"}
STATUS_COLORS = {
    "supported": COLORS["success"],
    "partial": COLORS["warning"],
    "no_evidence": COLORS["error"],
}


def _clean(text: str) -> str:
    """Collapse all whitespace into single spaces."""
    return " ".join(str(text).split())


def match_counts(result: JobMatchResult) -> dict[str, int]:
    """Totals per status, plus the number of requirements."""
    matches = result.matches
    counts = {"total": len(matches)}
    for status in STATUS_LABELS:
        counts[status] = sum(1 for m in matches if m.status == status)
    return counts


def build_match_figure(result: JobMatchResult) -> go.Figure:
    """Donut chart of requirement statuses."""
    counts = match_counts(result)
    statuses = list(STATUS_LABELS)
    fig = go.Figure(
        go.Pie(
            labels=[STATUS_LABELS[s] for s in statuses],
            values=[counts[s] for s in statuses],
            hole=0.6,
            sort=False,
            marker={"colors": [STATUS_COLORS[s] for s in statuses]},
            textinfo="value",
            hovertemplate="%{label}: %{value}<extra></extra>",
        )
    )
    _apply_dark_layout(fig, height=300)
    fig.update_layout(showlegend=True, legend={"font": {"color": COLORS["text"]}})
    return fig


def summary_html(result: JobMatchResult) -> str:
    """Card with the four counts."""
    c = match_counts(result)
    stats = (
        ("Requirements", c["total"]),
        ("Supported", c["supported"]),
        ("Partial", c["partial"]),
        ("No evidence", c["no_evidence"]),
    )
    boxes = "".join(
        f'<div class="riq-stat"><b>{count}</b><span>{escape(label)}</span></div>'
        for label, count in stats
    )
    return (
        '<div class="riq-card"><h3>Job match</h3>'
        "<p>Each requirement from the job description is checked against the "
        "resume. Supported means the resume shows it, partial means it is "
        "only partly shown, no evidence means nothing in the resume backs it up.</p>"
        f'<div class="riq-stats">{boxes}</div></div>'
    )


def details_html(result: JobMatchResult) -> str:
    """Card listing every requirement with its status and evidence. Escaped."""
    rows = []
    for item in result.matches:
        kind = STATUS_BADGE.get(item.status, "info")
        status = STATUS_LABELS.get(item.status, str(item.status))
        evidence = _clean(item.evidence) or "No evidence given."
        rows.append(
            "<li>"
            f"<b>{escape(_clean(item.requirement))}</b> {badge_html(status, kind)}<br>"
            f"<span style='color:var(--riq-muted)'>{escape(evidence)}</span>"
            "</li>"
        )
    return (
        '<div class="riq-card"><h3>Requirement details</h3>'
        f"<ul>{''.join(rows)}</ul></div>"
    )


def list_card_html(title: str, items: list[str]) -> str:
    """Bullet card, or an empty string when there is nothing to show."""
    if not items:
        return ""
    rows = "".join(f"<li>{escape(_clean(item))}</li>" for item in items)
    return f'<div class="riq-card"><h3>{escape(title)}</h3><ul>{rows}</ul></div>'


def render_job_match(result: JobMatchResult | None) -> None:
    """Draw the job-match section, or a clear message when none was computed."""
    if result is None:
        st.info(
            "No job description was provided, so no job match was computed. "
            "Paste one above and run the analysis again to see it."
        )
        return
    if result.matches:
        st.markdown(summary_html(result), unsafe_allow_html=True)
        st.plotly_chart(
            build_match_figure(result), width="stretch", config={"displayModeBar": False}
        )
        st.markdown(details_html(result), unsafe_allow_html=True)
    else:
        st.info("No requirements were extracted from the job description.")
    for title, items in (
        ("Experience to emphasize", result.experience_to_emphasize),
        ("Skills to develop", result.skills_to_develop),
    ):
        html = list_card_html(title, items)
        if html:
            st.markdown(html, unsafe_allow_html=True)