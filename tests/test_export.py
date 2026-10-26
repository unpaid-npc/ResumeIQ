"""Tests for the JSON and Markdown exports."""

import json

from backend.schemas import (
    BulletRewrite, Finding, FinalReport, JobMatchItem, JobMatchResult,
    QualityScores, ResumeEvaluation, SkillItem, SkillsAnalysis,
)
from ui.export import report_to_json, report_to_markdown


def make_report(with_job: bool = True, with_eval: bool = True) -> FinalReport:
    evaluation = None
    if with_eval:
        evaluation = ResumeEvaluation(
            scores=QualityScores(
                clarity=8, readability=7, organization=6, writing_quality=5,
                project_descriptions=4, achievement_language=3,
                quantification=2, completeness=9,
            ),
            strengths=[Finding(area="Clarity", observation="Clear", evidence="ev", suggestion=None)],
            improvements=[Finding(area="Numbers", observation="Few", evidence="ev2", suggestion="Add real numbers")],
        )
    job = None
    if with_job:
        job = JobMatchResult(
            matches=[JobMatchItem(requirement="Python", status="supported", evidence="Used it")],
            experience_to_emphasize=["Internship"],
            skills_to_develop=["SQL"],
        )
    return FinalReport(
        executive_summary="Solid start.",
        strengths=["Clean layout"],
        weaknesses=["No metrics"],
        skills=SkillsAnalysis(skills=[
            SkillItem(skill="Python", category="technical", status="demonstrated", evidence="Internship")
        ]),
        evaluation=evaluation,
        job_match=job,
        recommendations=["Add numbers"],
        bullet_rewrites=[BulletRewrite(original="Made reports", improved="Built reports", note="Verb")],
        next_steps=["Update resume"],
    )


def test_json_round_trips():
    report = make_report()
    text = report_to_json(report)
    json.loads(text)
    assert FinalReport.model_validate_json(text) == report


def test_json_round_trips_without_optional_parts():
    report = make_report(with_job=False, with_eval=False)
    assert FinalReport.model_validate_json(report_to_json(report)) == report


def test_markdown_has_every_section():
    md = report_to_markdown(make_report())
    for heading in ("# ResumeIQ Report", "## Executive summary", "## Strengths",
                    "## Weaknesses", "## Quality scores", "## Skills", "## Job match",
                    "## Recommendations", "## Next steps", "## Bullet rewrites",
                    "## Strengths in detail", "## Areas to improve in detail"):
        assert heading in md
    assert "Average: 5.5/10" in md
    assert "Before: Made reports" in md and "After: Built reports" in md
    assert "NOT checked" in md


def test_markdown_without_job_or_evaluation():
    md = report_to_markdown(make_report(with_job=False, with_eval=False))
    assert "no job match was computed" in md
    assert "Not available for this analysis." in md
    assert "## Strengths in detail" not in md


def test_markdown_with_no_rewrites_says_so():
    report = make_report()
    report = report.model_copy(update={"bullet_rewrites": []})
    assert "None kept for this analysis" in report_to_markdown(report)