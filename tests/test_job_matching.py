import json

import pytest

from backend.schemas import OutputValidationError, ParsedResume, SkillsAnalysis
from services import analysis_service
from services.analysis_service import (
    MAX_JOB_DESCRIPTION_CHARS,
    AnalysisError,
    analyze_resume,
    match_job_description,
)

SCORE_NAMES = [
    "clarity", "readability", "organization", "writing_quality",
    "project_descriptions", "achievement_language", "quantification", "completeness",
]
PARSED_JSON = '{"candidate": {"name": "Jane Doe"}, "technical_skills": ["Python"]}'
SKILLS_JSON = json.dumps({"skills": [
    {"skill": "Python", "category": "technical", "status": "demonstrated", "evidence": "Dashboard"}
]})
EVAL_JSON = json.dumps({"scores": {name: 6 for name in SCORE_NAMES}})
MATCH_JSON = json.dumps({
    "matches": [
        {"requirement": "Python", "status": "supported", "evidence": "Dashboard project"},
        {"requirement": "Tableau", "status": "partial", "evidence": "Listed only"},
        {"requirement": "Machine learning", "status": "no_evidence", "evidence": ""},
    ],
    "experience_to_emphasize": ["Sales Dashboard"],
    "skills_to_develop": ["Machine learning"],
})
JD = "We need a data analyst with Python, Tableau and machine learning."


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


def test_no_job_description_returns_none():
    for empty in (None, "", "   \n  "):
        assert match_job_description(ParsedResume(), SkillsAnalysis(), "resume", empty) is None


def test_valid_job_match(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: MATCH_JSON)
    result = match_job_description(ParsedResume(), SkillsAnalysis(), "resume", JD)
    assert [m.status for m in result.matches] == ["supported", "partial", "no_evidence"]
    assert result.skills_to_develop == ["Machine learning"]


def test_malformed_job_match_output(fake_setup, monkeypatch):
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: "I cannot do that")
    with pytest.raises(OutputValidationError):
        match_job_description(ParsedResume(), SkillsAnalysis(), "resume", JD)


def test_invalid_status_rejected(fake_setup, monkeypatch):
    bad = json.dumps({"matches": [{"requirement": "SQL", "status": "maybe"}]})
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: bad)
    with pytest.raises(OutputValidationError):
        match_job_description(ParsedResume(), SkillsAnalysis(), "resume", JD)


def test_job_match_retry_after_bad_output(fake_setup, monkeypatch):
    answers = iter(["not json", MATCH_JSON])
    monkeypatch.setattr(analysis_service, "_run_crew", lambda agents, tasks: next(answers))
    result = match_job_description(ParsedResume(), SkillsAnalysis(), "resume", JD)
    assert len(result.matches) == 3


def test_job_description_too_long():
    too_long = "x" * (MAX_JOB_DESCRIPTION_CHARS + 1)
    with pytest.raises(AnalysisError, match="too long"):
        match_job_description(ParsedResume(), SkillsAnalysis(), "resume", too_long)


def test_analyze_resume_without_job_description_skips_matcher(fake_setup, monkeypatch):
    answers = iter([PARSED_JSON, SKILLS_JSON, EVAL_JSON])
    calls = []

    def fake_run(agents, tasks):
        calls.append(1)
        return next(answers)

    monkeypatch.setattr(analysis_service, "_run_crew", fake_run)
    results = analyze_resume("Jane Doe resume")
    assert len(calls) == 3
    assert results.job_match is None


def test_analyze_resume_with_job_description_runs_matcher(fake_setup, monkeypatch):
    answers = iter([PARSED_JSON, SKILLS_JSON, EVAL_JSON, MATCH_JSON])
    calls = []

    def fake_run(agents, tasks):
        calls.append(1)
        return next(answers)

    monkeypatch.setattr(analysis_service, "_run_crew", fake_run)
    results = analyze_resume("Jane Doe resume", JD)
    assert len(calls) == 4
    assert results.job_match.matches[0].requirement == "Python"