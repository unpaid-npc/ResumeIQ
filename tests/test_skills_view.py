"""Tests for the skills counts, figure and HTML."""

from backend.schemas import SkillItem, SkillsAnalysis
from ui.skills import (
    build_skills_figure,
    category_counts,
    category_label,
    skill_counts,
    skills_list_html,
    summary_html,
)


def make_analysis() -> SkillsAnalysis:
    return SkillsAnalysis(
        skills=[
            SkillItem(skill="Python", category="technical", status="demonstrated",
                      evidence="Used Python in the internship."),
            SkillItem(skill="Pandas", category="data_analytics", status="demonstrated",
                      evidence="Cleaned datasets with Pandas."),
            SkillItem(skill="SQL", category="technical", status="mentioned_only",
                      evidence="Listed in the skills section only."),
            SkillItem(skill="<b>Tableau</b>", category="data_analytics", status="mentioned_only",
                      evidence="Listed in the skills section only."),
        ]
    )


def test_skill_counts():
    assert skill_counts(make_analysis()) == {
        "total": 4,
        "demonstrated": 2,
        "mentioned_only": 2,
        "categories": 2,
    }


def test_category_counts_split_by_status():
    counts = category_counts(make_analysis())
    assert counts["technical"] == {"demonstrated": 1, "mentioned_only": 1}
    assert counts["data_analytics"] == {"demonstrated": 1, "mentioned_only": 1}
    assert list(counts) == ["technical", "data_analytics"]  # display order


def test_empty_analysis_counts_are_zero():
    empty = SkillsAnalysis.model_construct(skills=[])
    assert skill_counts(empty)["total"] == 0
    assert category_counts(empty) == {}


def test_figure_has_two_stacked_traces():
    fig = build_skills_figure(make_analysis())
    assert [t.name for t in fig.data] == ["Demonstrated", "Mentioned only"]
    assert list(fig.data[0].x) == [1, 1]
    assert fig.layout.barmode == "stack"


def test_skill_list_escapes_html():
    html = skills_list_html(make_analysis())
    assert "&lt;b&gt;Tableau&lt;/b&gt;" in html
    assert "<b>Tableau</b>" not in html


def test_summary_shows_counts_and_labels():
    html = summary_html(make_analysis())
    for text in ("Skills found", "Demonstrated", "Mentioned only", "Categories"):
        assert text in html


def test_unknown_category_gets_a_readable_label():
    assert category_label("domain_specific") == "Domain specific"
    assert category_label("new_thing") == "New Thing"