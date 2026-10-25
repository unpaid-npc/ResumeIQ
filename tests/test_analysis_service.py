import pytest

from backend.schemas import OutputValidationError
from services import analysis_service
from services.analysis_service import AnalysisError, parse_resume


@pytest.fixture
def fake_setup(monkeypatch):
    """Replace the real LLM, agent and task so tests never call the internet."""
    monkeypatch.setattr(analysis_service, "get_llm", lambda: object())
    monkeypatch.setattr(analysis_service, "create_resume_parser_agent", lambda llm: object())
    monkeypatch.setattr(analysis_service, "create_parse_task", lambda agent, text: object())


def test_empty_text_rejected():
    with pytest.raises(AnalysisError, match="empty"):
        parse_resume("   ")


def test_valid_model_output(fake_setup, monkeypatch):
    monkeypatch.setattr(
        analysis_service, "_run_crew",
        lambda agents, tasks: '{"candidate": {"name": "Jane Doe"}, "technical_skills": ["Python"]}',
    )
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