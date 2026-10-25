"""Result sections drawn with Streamlit (scores for now)."""

from html import escape

import streamlit as st

from backend.schemas import QualityScores, ResumeEvaluation
from ui.charts import (
    LEVEL_BADGE,
    average_score,
    build_bar_figure,
    build_radar_figure,
    score_items,
    score_level,
)
from ui.components import badge_html


def scores_html(scores: QualityScores) -> str:
    """Build the score card: average badge and one box per score."""
    average = average_score(scores)
    badge = badge_html(f"Average {average}/10", LEVEL_BADGE[score_level(average)])
    boxes = "".join(
        f'<div class="riq-stat riq-score-{score_level(value)}">'
        f"<b>{value}</b><span>{escape(label)}</span></div>"
        for label, value in score_items(scores)
    )
    return (
        '<div class="riq-card"><h3>Quality scores</h3>'
        "<p>Scores from 0 to 10, estimated by the AI. They can vary a little "
        "between runs, so treat them as guidance, not a verdict.</p>"
        f'<div class="riq-scores">{boxes}</div>'
        f'<div style="margin-top:1rem">{badge}</div></div>'
    )


def render_scores(evaluation: ResumeEvaluation | None) -> None:
    """Draw the score card and both charts, or a clear message if missing."""
    if evaluation is None:
        st.info("Quality scores are not available for this analysis.")
        return
    scores = evaluation.scores
    st.markdown(scores_html(scores), unsafe_allow_html=True)
    left, right = st.columns(2)
    chart_config = {"displayModeBar": False}
    with left:
        st.plotly_chart(build_radar_figure(scores), width="stretch", config=chart_config)
    with right:
        st.plotly_chart(build_bar_figure(scores), width="stretch", config=chart_config)