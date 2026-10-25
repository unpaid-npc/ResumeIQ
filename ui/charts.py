"""Score numbers and dark-styled Plotly figures for the quality scores.

No Streamlit code here, so everything can be tested on its own.
"""

import plotly.graph_objects as go

from backend.schemas import QualityScores
from ui.styles import COLORS, FONT_STACK

# Schema field name -> label shown to the user, in display order.
SCORE_LABELS = {
    "clarity": "Clarity",
    "readability": "Readability",
    "organization": "Organization",
    "writing_quality": "Writing quality",
    "project_descriptions": "Project descriptions",
    "achievement_language": "Achievement language",
    "quantification": "Quantification",
    "completeness": "Completeness",
}

MAX_SCORE = 10
LEVEL_COLORS = {
    "high": COLORS["success"],
    "mid": COLORS["warning"],
    "low": COLORS["error"],
}
LEVEL_BADGE = {"high": "success", "mid": "warning", "low": "error"}


def score_items(scores: QualityScores) -> list[tuple[str, int]]:
    """Return (label, value) pairs in display order."""
    return [(label, int(getattr(scores, field))) for field, label in SCORE_LABELS.items()]


def average_score(scores: QualityScores) -> float:
    """Average of the eight scores, rounded to one decimal."""
    values = [value for _, value in score_items(scores)]
    return round(sum(values) / len(values), 1)


def score_level(value: float) -> str:
    """'high' for 7 and above, 'mid' for 5 to 6.9, otherwise 'low'."""
    if value >= 7:
        return "high"
    if value >= 5:
        return "mid"
    return "low"


def _wrap_label(label: str) -> str:
    """Put a line break after the first word of a long label (for the radar)."""
    if len(label) > 12 and " " in label:
        return label.replace(" ", "<br>", 1)
    return label


def _apply_dark_layout(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"color": COLORS["text"], "family": FONT_STACK, "size": 13},
        margin={"l": 10, "r": 30, "t": 30, "b": 10},
        height=height,
        showlegend=False,
    )
    return fig


def build_bar_figure(scores: QualityScores) -> go.Figure:
    """Horizontal bars, one per score, colored by level."""
    items = score_items(scores)
    labels = [label for label, _ in items]
    values = [value for _, value in items]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            text=values,
            textposition="outside",
            marker_color=[LEVEL_COLORS[score_level(v)] for v in values],
            hovertemplate="%{y}: %{x}/10<extra></extra>",
        )
    )
    fig.update_xaxes(
        range=[0, MAX_SCORE + 1], gridcolor=COLORS["border"], zeroline=False
    )
    fig.update_yaxes(autorange="reversed")
    return _apply_dark_layout(fig, height=360)


def build_radar_figure(scores: QualityScores) -> go.Figure:
    """Radar (spider) chart of the eight scores."""
    items = score_items(scores)
    labels = [_wrap_label(label) for label, _ in items]
    values = [value for _, value in items]
    # Repeat the first point so the shape closes.
    fig = go.Figure(
        go.Scatterpolar(
            r=values + values[:1],
            theta=labels + labels[:1],
            fill="toself",
            line={"color": COLORS["primary"], "width": 2},
            fillcolor="rgba(138,180,248,0.25)",
            hovertemplate="%{theta}: %{r}/10<extra></extra>",
        )
    )
    fig.update_layout(
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {
                "range": [0, MAX_SCORE],
                "gridcolor": COLORS["border"],
                "linecolor": COLORS["border"],
                "tickfont": {"color": COLORS["muted"]},
            },
            "angularaxis": {"gridcolor": COLORS["border"], "linecolor": COLORS["border"]},
        }
    )
    _apply_dark_layout(fig, height=380)
    # Wider side margins so long labels are not cut off.
    fig.update_layout(margin={"l": 90, "r": 90, "t": 30, "b": 30})
    return fig