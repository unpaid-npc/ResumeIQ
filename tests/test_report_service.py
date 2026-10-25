import json

import pytest
from pydantic import ValidationError

from backend.schemas import (
    BulletRewrite,
    FeedbackDraft,
    OutputValidationError,
    ParsedResume,
    QualityScores,
    ResumeEvaluation,
    SkillsAnalysis,
)
from services import analysis_service, report_service
from services.analysis_service import AnalysisError, AnalysisResults
from services.report_service import (
    build_final_report,
    filter_bullet_rewrites,
    run_full_analysis,
)

SCORE_NAMES = [
    "clarity", "readability", "organization", "writing_quality",
    "project_descriptions", "achievement_language", "quantification", "completeness",
]
RESUME = "Jane Doe\n- Built a sales dashboard using Python\n- Analyzed 10,000 records to find top products\n"
JD = "We need a data analyst with Python and machine learning."

PARSED_JSON = '{"candidate": {"name": "Jane Doe"}, "technical_skills": ["Python"]}'
SKILLS_JSON = json.dumps({"skills": [
    {"skill": "Python", "category": "technical", "status": "demonstrated", "evidence": "Dashboard"}
]})
EVAL_JSON = json.dumps({"scores": {name: 6 for name in SCORE_NAMES}})
MATCH_JSON = json.dumps({
    "matches": [{"requirement": "Python", "status": "supported", "evidence": "Dashboard"}],
})


def feedback_json(improved="Developed a sales dashboard in Python"):
    return json.dumps({
        "executive_summary": "A solid early-career resume.",
        "strengths": ["Clear structure"],
        "weaknesses": ["Few numbers"],
        "recommendations": ["Add real numbers where you have them"],
        "bullet_rewrites": [{
            "original": "Built a sales dashboard using Python",
            "improved": improved,
            "note": "",
        }],
        "next_steps": ["Add a phone number"],
    })


def rewrite(original, improved):
    return BulletRewrite(original=original, improved=improved)


@pytest.fixture
def fake_setup(monkeypatch):
    """Replace the real LLM, agents and tasks so tests never call the internet."""
    monkeypatch.setattr(analysis_service, "get_llm", lambda: object())
    monkeypatch.setattr(analysis_service, "create_resume_parser_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_parse_task", lambda a, t: object())
    monkeypatch.setattr(analysis_service, "create_skills_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_skills_task", lambda a, p, t: object())
    monkeypatch.setattr(analysis_service, "create_evaluator_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_evaluation_task", lambda a, p, s, t: object())
    monkeypatch.setattr(analysis_service, "create_job_match_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_job_match_task", lambda a, p, s, t, j: object())
    monkeypatch.setattr(report_service, "get_llm", lambda: object())
    monkeypatch.setattr(report_service, "create_feedback_agent", lambda llm: object())
    monkeypatch.setattr(report_service, "create_feedback_task", lambda a, p, s, e, j, t: object())


def sequence(monkeypatch, answers):
    """Make the fake model return the given answers in order; count the calls."""
    remaining = iter(answers)
    calls = []

    def fake_run(agents, tasks):
        calls.append(1)
        return next(remaining)

    monkeypatch.setattr(analysis_service, "_run_crew", fake_run)
    return calls


def test_keeps_faithful_rewrite():
    r = rewrite("Built a sales dashboard using Python", "Developed a sales dashboard in Python")
    assert filter_bullet_rewrites([r], RESUME) == [r]


def test_drops_rewrite_with_unknown_original():
    r = rewrite("Led a team of engineers", "Directed an engineering team")
    assert filter_bullet_rewrites([r], RESUME) == []


def test_drops_rewrite_with_invented_number():
    r = rewrite("Built a sales dashboard using Python", "Built a Python dashboard used by 500 managers")
    assert filter_bullet_rewrites([r], RESUME) == []


def test_keeps_rewrite_with_number_from_resume():
    r = rewrite(
        "Analyzed 10,000 records to find top products",
        "Analyzed 10000 records to identify best-selling products",
    )
    assert filter_bullet_rewrites([r], RESUME) == [r]


def test_feedback_draft_requires_summary():
    with pytest.raises(ValidationError):
        FeedbackDraft()
    with pytest.raises(ValidationError):
        FeedbackDraft(executive_summary="   ")


def test_build_final_report_copies_structured_data():
    results = AnalysisResults(
        parsed=ParsedResume(),
        skills=SkillsAnalysis(),
        evaluation=ResumeEvaluation(scores=QualityScores(**{n: 6 for n in SCORE_NAMES})),
        job_match=None,
    )
    draft = FeedbackDraft(executive_summary="Good.", recommendations=["Add numbers"])
    report = build_final_report(results, draft, RESUME)
    assert report.executive_summary == "Good."
    assert report.evaluation.scores.clarity == 6
    assert report.job_match is None
    assert report.recommendations == ["Add numbers"]


def test_full_analysis_without_job_description(fake_setup, monkeypatch):
    calls = sequence(monkeypatch, [PARSED_JSON, SKILLS_JSON, EVAL_JSON, feedback_json()])
    report = run_full_analysis(RESUME)
    assert len(calls) == 4
    assert report.job_match is None
    assert report.skills.skills[0].skill == "Python"
    assert report.evaluation.scores.clarity == 6
    assert len(report.bullet_rewrites) == 1


def test_full_analysis_with_job_description(fake_setup, monkeypatch):
    calls = sequence(
        monkeypatch, [PARSED_JSON, SKILLS_JSON, EVAL_JSON, MATCH_JSON, feedback_json()]
    )
    report = run_full_analysis(RESUME, JD)
    assert len(calls) == 5
    assert report.job_match.matches[0].status == "supported"


def test_malformed_feedback_output(fake_setup, monkeypatch):
    sequence(monkeypatch, [PARSED_JSON, SKILLS_JSON, EVAL_JSON, "not json", "still not json"])
    with pytest.raises(OutputValidationError):
        run_full_analysis(RESUME)


def test_full_analysis_empty_resume():
    with pytest.raises(AnalysisError, match="empty"):
        run_full_analysis("")


def test_invented_rewrite_is_dropped_in_full_report(fake_setup, monkeypatch):
    invented = feedback_json(improved="Built a Python dashboard used by 500 managers")
    sequence(monkeypatch, [PARSED_JSON, SKILLS_JSON, EVAL_JSON, invented])
    report = run_full_analysis(RESUME)
    assert report.bullet_rewrites == []