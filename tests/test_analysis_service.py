import json

import pytest

from backend.schemas import OutputValidationError, ParsedResume, SkillsAnalysis
from services import analysis_service
from services.analysis_service import (
    AnalysisError,
    analyze_resume,
    analyze_skills,
    evaluate_resume,
    parse_resume,
)

SCORE_NAMES = [
    "clarity", "readability", "organization", "writing_quality",
    "project_descriptions", "achievement_language", "quantification", "completeness",
]

PARSED_JSON = '{"candidate": {"name": "Jane Doe"}, "technical_skills": ["Python"]}'
SKILLS_JSON = json.dumps({"skills": [
    {"skill": "Python", "category": "technical", "status": "demonstrated", "evidence": "Sales Dashboard"}
]})


def evaluation_json(score=7):
    return json.dumps({
        "scores": {name: score for name in SCORE_NAMES},
        "strengths": [{"area": "Skills", "observation": "Clear skills list"}],
        "improvements": [{"area": "Numbers", "observation": "Few metrics", "suggestion": "Add real numbers"}],
    })


@pytest.fixture
def fake_setup(monkeypatch):
    """Replace the real LLM, agents and tasks so tests never call the internet."""
    monkeypatch.setattr(analysis_service, "get_llm", lambda: object())
    monkeypatch.setattr(analysis_service, "create_resume_parser_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_parse_task", lambda agent, text: object())
    monkeypatch.setattr(analysis_service, "create_skills_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_skills_task", lambda agent, parsed, text: object())
    monkeypatch.setattr(analysis_service, "create_evaluator_agent", lambda llm: object())
    monkeypatch.setattr(
        analysis_service, "create_evaluation_task", lambda agent, parsed, skills, text: object()
    )


def test_empty_text_rejected():
    with pytest.raises(AnalysisError, match="empty"):
        parse_resume("   ")


def test_valid_model_output(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: PARSED_JSON)
    result = parse_resume("Jane Doe, Python developer")
    assert result.candidate.name == "Jane Doe"
    assert result.technical_skills == ["Python"]


def test_fenced_model_output(fake_setup, monkeypatch):
    monkeypatch.setattr(
        analysis_service, "_run_crew",
        lambda agents, tasks: '```json\n{"technical_skills": ["SQL"]}\n```',
    )
    assert parse_resume("some resume").technical_skills == ["SQL"]


def test_malformed_model_output(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: "Sorry, I cannot do that.")
    with pytest.raises(OutputValidationError):
        parse_resume("some resume")


def test_malformed_then_valid_retries(fake_setup, monkeypatch):
    answers = iter(["not json at all", PARSED_JSON])
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: next(answers))
    assert parse_resume("some resume").candidate.name == "Jane Doe"


def test_analyze_skills_valid(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: SKILLS_JSON)
    result = analyze_skills(ParsedResume(), "resume text")
    assert result.skills[0].status == "demonstrated"


def test_analyze_skills_malformed(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: '{"skills": "oops"}')
    with pytest.raises(OutputValidationError):
        analyze_skills(ParsedResume(), "resume text")


def test_evaluate_resume_valid(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: evaluation_json(8))
    result = evaluate_resume(ParsedResume(), SkillsAnalysis(), "resume text")
    assert result.scores.clarity == 8
    assert result.improvements[0].suggestion == "Add real numbers"


def test_evaluate_resume_score_out_of_range(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: evaluation_json(11))
    with pytest.raises(OutputValidationError):
        evaluate_resume(ParsedResume(), SkillsAnalysis(), "resume text")


def test_analyze_resume_runs_all_stages_in_order(fake_setup, monkeypatch):
    answers = iter([PARSED_JSON, SKILLS_JSON, evaluation_json(6)])
    calls = []

    def fake_run(agents, tasks):
        calls.append(1)
        return next(answers)

    monkeypatch.setattr(analysis_service, "_run_crew", fake_run)
    results = analyze_resume("Jane Doe resume")
    assert len(calls) == 3
    assert results.parsed.candidate.name == "Jane Doe"
    assert results.skills.skills[0].skill == "Python"
    assert results.evaluation.scores.completeness == 6


def test_analyze_resume_empty_text():
    with pytest.raises(AnalysisError, match="empty"):
        analyze_resume("")