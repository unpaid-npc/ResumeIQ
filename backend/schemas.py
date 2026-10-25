"""Data models (blueprints) for everything the ResumeIQ agents produce.

Rule: optional fields default to empty, so the AI is never forced to invent data.
"""
import json
import re
from typing import Literal, Type, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class OutputValidationError(Exception):
    """Raised when AI output is empty, not JSON, or has the wrong structure."""


class ResumeBase(BaseModel):
    # Ignore unexpected extra keys the AI may add; trim stray whitespace.
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


# ---------- Agent 1: Resume Parser ----------
class CandidateInfo(ResumeBase):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] = Field(default_factory=list)


class Education(ResumeBase):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    grade: str | None = None


class Experience(ResumeBase):
    company: str
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    is_internship: bool = False
    bullets: list[str] = Field(default_factory=list)


class Project(ResumeBase):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class Certification(ResumeBase):
    name: str
    issuer: str | None = None
    date: str | None = None


class ParsedResume(ResumeBase):
    candidate: CandidateInfo = Field(default_factory=CandidateInfo)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    technical_skills: list[str] = Field(default_factory=list)
    business_skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


# ---------- Agent 2: Skills Analysis ----------
SkillCategory = Literal[
    "technical",
    "data_analytics",
    "business_analytics",
    "communication",
    "leadership",
    "domain_specific",
]
SkillStatus = Literal["demonstrated", "mentioned_only"]


class SkillItem(ResumeBase):
    skill: str
    category: SkillCategory
    status: SkillStatus  # demonstrated = backed by a project/job; mentioned_only = just listed
    evidence: str = ""


class SkillsAnalysis(ResumeBase):
    skills: list[SkillItem] = Field(default_factory=list)


# ---------- Agent 3: Resume Evaluation ----------
class QualityScores(ResumeBase):
    clarity: int = Field(ge=0, le=10)
    readability: int = Field(ge=0, le=10)
    organization: int = Field(ge=0, le=10)
    writing_quality: int = Field(ge=0, le=10)
    project_descriptions: int = Field(ge=0, le=10)
    achievement_language: int = Field(ge=0, le=10)
    quantification: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)


class Finding(ResumeBase):
    area: str
    observation: str
    evidence: str = ""
    suggestion: str | None = None


class ResumeEvaluation(ResumeBase):
    scores: QualityScores
    strengths: list[Finding] = Field(default_factory=list)
    improvements: list[Finding] = Field(default_factory=list)


# ---------- Agent 4: Job Matching (optional) ----------
MatchStatus = Literal["supported", "partial", "no_evidence"]


class JobMatchItem(ResumeBase):
    requirement: str
    status: MatchStatus
    evidence: str = ""


class JobMatchResult(ResumeBase):
    matches: list[JobMatchItem] = Field(default_factory=list)
    experience_to_emphasize: list[str] = Field(default_factory=list)
    skills_to_develop: list[str] = Field(default_factory=list)


# ---------- Agent 5: Final Report ----------
class BulletRewrite(ResumeBase):
    original: str
    improved: str
    note: str = ""


class FinalReport(ResumeBase):
    executive_summary: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    skills: SkillsAnalysis = Field(default_factory=SkillsAnalysis)
    evaluation: ResumeEvaluation | None = None
    job_match: JobMatchResult | None = None  # None when no job description was given
    recommendations: list[str] = Field(default_factory=list)
    bullet_rewrites: list[BulletRewrite] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)


# ---------- Safe parsing of raw AI output ----------
T = TypeVar("T", bound=BaseModel)


def parse_model_output(model_class: Type[T], raw: str) -> T:
    """Turn raw AI text (JSON, possibly in ```json fences) into a validated model."""
    if not raw or not raw.strip():
        raise OutputValidationError("The model returned an empty response.")
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise OutputValidationError("The model output is not valid JSON.") from exc
    try:
        return model_class.model_validate(data)
    except ValidationError as exc:
        raise OutputValidationError(
            f"The model output has the wrong structure ({exc.error_count()} problem(s))."
        ) from exc

# ---------- Agent 5 output: written feedback only ----------
class FeedbackDraft(ResumeBase):
    """What the Feedback agent writes. Skills, scores and job match are copied
    from earlier agents by our own code, never rewritten by the model."""

    executive_summary: str = Field(min_length=1)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    bullet_rewrites: list[BulletRewrite] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)