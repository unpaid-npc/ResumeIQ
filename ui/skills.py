"""Skills section: counts, a category chart and a readable skill list."""

from html import escape

import plotly.graph_objects as go
import streamlit as st

from backend.schemas import SkillsAnalysis
from ui.charts import _apply_dark_layout
from ui.components import badge_html
from ui.styles import COLORS

CATEGORY_LABELS = {
    "technical": "Technical",
    "data_analytics": "Data analytics",
    "business_analytics": "Business analytics",
    "communication": "Communication",
    "leadership": "Leadership",
    "domain_specific": "Domain specific",
}
STATUS_LABELS = {"demonstrated": "Demonstrated", "mentioned_only": "Mentioned only"}
STATUS_BADGE = {"demonstrated": "success", "mentioned_only": "warning"}


def _clean(text: str) -> str:
    """Collapse all whitespace into single spaces."""
    return " ".join(str(text).split())


def category_label(category: str) -> str:
    """Friendly name for a category, with a fallback for unknown ones."""
    return CATEGORY_LABELS.get(category, str(category).replace("_", " ").title())


def skill_counts(analysis: SkillsAnalysis) -> dict[str, int]:
    """Totals: skills found, demonstrated, mentioned only, categories used."""
    skills = analysis.skills
    return {
        "total": len(skills),
        "demonstrated": sum(1 for s in skills if s.status == "demonstrated"),
        "mentioned_only": sum(1 for s in skills if s.status == "mentioned_only"),
        "categories": len({s.category for s in skills}),
    }


def category_counts(analysis: SkillsAnalysis) -> dict[str, dict[str, int]]:
    """Per category: how many skills are demonstrated / mentioned only."""
    result: dict[str, dict[str, int]] = {}
    for skill in analysis.skills:
        row = result.setdefault(skill.category, {"demonstrated": 0, "mentioned_only": 0})
        if skill.status in row:
            row[skill.status] += 1
    ordered = {c: result[c] for c in CATEGORY_LABELS if c in result}
    ordered.update({c: v for c, v in result.items() if c not in ordered})
    return ordered


def build_skills_figure(analysis: SkillsAnalysis) -> go.Figure:
    """Stacked horizontal bars: skills per category, split by status."""
    counts = category_counts(analysis)
    labels = [category_label(c) for c in counts]
    fig = go.Figure()
    colors = {"demonstrated": COLORS["success"], "mentioned_only": COLORS["warning"]}
    for status in ("demonstrated", "mentioned_only"):
        fig.add_trace(
            go.Bar(
                name=STATUS_LABELS[status],
                y=labels,
                x=[row[status] for row in counts.values()],
                orientation="h",
                marker_color=colors[status],
                hovertemplate="%{y}: %{x} " + STATUS_LABELS[status].lower() + "<extra></extra>",
            )
        )
    fig.update_layout(barmode="stack")
    fig.update_xaxes(gridcolor=COLORS["border"], zeroline=False, dtick=1)
    fig.update_yaxes(autorange="reversed")
    _apply_dark_layout(fig, height=max(240, 70 + 48 * len(labels)))
    fig.update_layout(
        showlegend=True,
        legend={"orientation": "h", "y": 1.15, "x": 0, "traceorder": "normal"},
    )
    return fig


def summary_html(analysis: SkillsAnalysis) -> str:
    """Card with the four counts."""
    c = skill_counts(analysis)
    stats = (
        ("Skills found", c["total"]),
        ("Demonstrated", c["demonstrated"]),
        ("Mentioned only", c["mentioned_only"]),
        ("Categories", c["categories"]),
    )
    boxes = "".join(
        f'<div class="riq-stat"><b>{count}</b><span>{escape(label)}</span></div>'
        for label, count in stats
    )
    return (
        '<div class="riq-card"><h3>Skills</h3>'
        "<p>Demonstrated means the resume shows the skill in use. Mentioned only "
        "means it is listed but the resume gives no supporting evidence.</p>"
        f'<div class="riq-stats">{boxes}</div></div>'
    )


def skills_list_html(analysis: SkillsAnalysis) -> str:
    """Card listing every skill with its status and evidence. All text escaped."""
    rows = []
    for skill in analysis.skills:
        kind = STATUS_BADGE.get(skill.status, "info")
        status = STATUS_LABELS.get(skill.status, str(skill.status))
        evidence = _clean(skill.evidence) or "No evidence given."
        rows.append(
            "<li>"
            f"<b>{escape(_clean(skill.skill))}</b> "
            f"<span style='color:var(--riq-muted)'>({escape(category_label(skill.category))})</span> "
            f"{badge_html(status, kind)}<br>"
            f"<span style='color:var(--riq-muted)'>{escape(evidence)}</span>"
            "</li>"
        )
    return (
        '<div class="riq-card"><h3>Skill details</h3>'
        f"<ul>{''.join(rows)}</ul></div>"
    )


def render_skills(analysis: SkillsAnalysis) -> None:
    """Draw the skills section, or a clear message when no skills were found."""
    if not analysis.skills:
        st.info("No skills were identified in this analysis.")
        return
    st.markdown(summary_html(analysis), unsafe_allow_html=True)
    st.plotly_chart(
        build_skills_figure(analysis), width="stretch", config={"displayModeBar": False}
    )
    st.markdown(skills_list_html(analysis), unsafe_allow_html=True)