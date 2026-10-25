import pytest
from pydantic import ValidationError

from backend.schemas import (
    Education,
    FinalReport,
    JobMatchItem,
    OutputValidationError,
    ParsedResume,
    QualityScores,
    SkillItem,
    SkillsAnalysis,
    parse_model_output,
)

SCORE_NAMES = [
    "clarity", "readability", "organization", "writing_quality",
    "project_descriptions", "achievement_language", "quantification", "completeness",
]


def valid_scores(value=7):
    return {name: value for name in SCORE_NAMES}


def test_parsed_resume_empty_defaults():
    resume = ParsedResume()
    assert resume.education == []
    assert resume.technical_skills == []
    assert resume.candidate.name is None


def test_parsed_resume_valid_data():
    resume = ParsedResume(
        candidate={"name": "Jane Doe"},
        education=[{"institution": "Test University", "degree": "BSc"}],
        experience=[{"company": "Acme", "is_internship": True}],
        technical_skills=["Python", "SQL"],
    )
    assert resume.candidate.name == "Jane Doe"
    assert resume.experience[0].is_internship is True
    assert resume.education[0].grade is None


def test_extra_fields_ignored():
    resume = ParsedResume.model_validate({"technical_skills": ["Python"], "unknown": 123})
    assert resume.technical_skills == ["Python"]
    assert not hasattr(resume, "unknown")


def test_education_requires_institution():
    with pytest.raises(ValidationError):
        Education(degree="BSc")


def test_score_out_of_range():
    with pytest.raises(ValidationError):
        QualityScores(**valid_scores(11))
    with pytest.raises(ValidationError):
        QualityScores(**valid_scores(-1))


def test_invalid_skill_status():
    with pytest.raises(ValidationError):
        SkillItem(skill="Python", category="technical", status="expert")


def test_job_match_status_validation():
    with pytest.raises(ValidationError):
        JobMatchItem(requirement="SQL", status="maybe")


def test_final_report_without_job_match():
    report = FinalReport(executive_summary="A solid resume.")
    assert report.job_match is None
    assert report.recommendations == []


def test_parse_valid_json():
    raw = '{"skills": [{"skill": "Python", "category": "technical", "status": "demonstrated", "evidence": "Built a project"}]}'
    result = parse_model_output(SkillsAnalysis, raw)
    assert result.skills[0].skill == "Python"


def test_parse_fenced_json():
    raw = '```json\n{"technical_skills": ["Python"]}\n```'
    result = parse_model_output(ParsedResume, raw)
    assert result.technical_skills == ["Python"]


def test_parse_invalid_json():
    with pytest.raises(OutputValidationError, match="not valid JSON"):
        parse_model_output(ParsedResume, "Sorry, I cannot help with that.")


def test_parse_empty_output():
    with pytest.raises(OutputValidationError, match="empty"):
        parse_model_output(ParsedResume, "   ")


def test_parse_wrong_structure():
    with pytest.raises(OutputValidationError, match="wrong structure"):
        parse_model_output(SkillsAnalysis, '{"skills": "not a list"}')