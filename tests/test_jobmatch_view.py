"""Tests for the job-match counts, figure and HTML."""

from backend.schemas import JobMatchItem, JobMatchResult
from ui.jobmatch import (
    build_match_figure,
    details_html,
    list_card_html,
    match_counts,
    summary_html,
)


def make_result() -> JobMatchResult:
    return JobMatchResult(
        matches=[
            JobMatchItem(requirement="Python", status="supported", evidence="Used in internship."),
            JobMatchItem(requirement="SQL", status="partial", evidence="Listed, no project."),
            JobMatchItem(requirement="<i>A/B testing</i>", status="no_evidence", evidence="Not found."),
            JobMatchItem(requirement="Excel", status="supported", evidence="Weekly report."),
        ],
        experience_to_emphasize=["Weekly Excel report for the team"],
        skills_to_develop=["A/B testing"],
    )


def test_match_counts():
    assert match_counts(make_result()) == {
        "total": 4,
        "supported": 2,
        "partial": 1,
        "no_evidence": 1,
    }


def test_empty_result_counts_are_zero():
    empty = JobMatchResult.model_construct(
        matches=[], experience_to_emphasize=[], skills_to_develop=[]
    )
    assert match_counts(empty)["total"] == 0


def test_figure_values_follow_status_order():
    fig = build_match_figure(make_result())
    assert list(fig.data[0].labels) == ["Supported", "Partial", "No evidence"]
    assert list(fig.data[0].values) == [2, 1, 1]


def test_details_escape_html():
    html = details_html(make_result())
    assert "&lt;i&gt;A/B testing&lt;/i&gt;" in html
    assert "<i>A/B testing</i>" not in html


def test_summary_shows_labels():
    html = summary_html(make_result())
    for text in ("Requirements", "Supported", "Partial", "No evidence"):
        assert text in html


def test_list_card_empty_and_escaped():
    assert list_card_html("Skills to develop", []) == ""
    html = list_card_html("Tips", ["<b>x</b>"])
    assert "&lt;b&gt;x&lt;/b&gt;" in html