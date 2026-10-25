"""Tests for the score helpers, figures and score card HTML."""

from backend.schemas import QualityScores
from ui.charts import (
    SCORE_LABELS,
    average_score,
    build_bar_figure,
    build_radar_figure,
    score_items,
    score_level,
)
from ui.results import scores_html


def make_scores() -> QualityScores:
    return QualityScores(
        clarity=8,
        readability=7,
        organization=6,
        writing_quality=5,
        project_descriptions=4,
        achievement_language=3,
        quantification=2,
        completeness=9,
    )


def test_score_items_follow_display_order():
    items = score_items(make_scores())
    assert [label for label, _ in items] == list(SCORE_LABELS.values())
    assert [value for _, value in items] == [8, 7, 6, 5, 4, 3, 2, 9]


def test_average_score_is_rounded_to_one_decimal():
    assert average_score(make_scores()) == 5.5


def test_score_levels():
    assert score_level(7) == "high"
    assert score_level(6.9) == "mid"
    assert score_level(5) == "mid"
    assert score_level(4.9) == "low"


def test_bar_figure_has_all_scores():
    fig = build_bar_figure(make_scores())
    assert list(fig.data[0].x) == [8, 7, 6, 5, 4, 3, 2, 9]
    assert len(fig.data[0].y) == 8


def test_radar_figure_closes_the_shape():
    fig = build_radar_figure(make_scores())
    r = list(fig.data[0].r)
    assert len(r) == 9
    assert r[0] == r[-1]


def test_figures_use_transparent_dark_layout():
    for fig in (build_bar_figure(make_scores()), build_radar_figure(make_scores())):
        assert fig.layout.paper_bgcolor == "rgba(0,0,0,0)"


def test_scores_html_shows_average_and_every_label():
    html = scores_html(make_scores())
    assert "Average 5.5/10" in html
    for label in SCORE_LABELS.values():
        assert label in html