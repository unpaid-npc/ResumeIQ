"""Combines all agent outputs into one validated final report."""
import re

from agents.feedback_generator import create_feedback_agent
from backend.schemas import BulletRewrite, FeedbackDraft, FinalReport
from services.analysis_service import AnalysisResults, _run_stage, analyze_resume
from services.llm_config import get_llm
from tasks.feedback_task import create_feedback_task


def _normalize(text: str) -> str:
    """Lowercase, drop punctuation and extra spaces so lines can be compared fairly."""
    text = re.sub(r"[^\w\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def _numbers(text: str) -> set[str]:
    """All numbers in a text, with thousands commas removed (10,000 -> 10000)."""
    return {n.replace(",", "") for n in re.findall(r"\d+(?:[.,]\d+)*", text)}


def filter_bullet_rewrites(
    rewrites: list[BulletRewrite], resume_text: str
) -> list[BulletRewrite]:
    """Keep only rewrites that are faithful to the resume.

    A rewrite is dropped when its original line is not really in the resume,
    or when the improved line contains a number that the resume does not contain.
    """
    resume_norm = _normalize(resume_text)
    resume_numbers = _numbers(resume_text)
    kept = []
    for rewrite in rewrites:
        original = _normalize(rewrite.original)
        if not original or original not in resume_norm:
            continue
        if not _numbers(rewrite.improved) <= resume_numbers:
            continue
        kept.append(rewrite)
    return kept


def generate_feedback(results: AnalysisResults, resume_text: str) -> FeedbackDraft:
    llm = get_llm()

    def make():
        agent = create_feedback_agent(llm)
        task = create_feedback_task(
            agent, results.parsed, results.skills, results.evaluation,
            results.job_match, resume_text,
        )
        return agent, task

    return _run_stage(FeedbackDraft, make)


def build_final_report(
    results: AnalysisResults, draft: FeedbackDraft, resume_text: str
) -> FinalReport:
    """Structured data comes from the earlier agents; the model only supplies the words."""
    return FinalReport(
        executive_summary=draft.executive_summary,
        strengths=draft.strengths,
        weaknesses=draft.weaknesses,
        skills=results.skills,
        evaluation=results.evaluation,
        job_match=results.job_match,
        recommendations=draft.recommendations,
        bullet_rewrites=filter_bullet_rewrites(draft.bullet_rewrites, resume_text),
        next_steps=draft.next_steps,
    )


def run_full_analysis(resume_text: str, job_description: str | None = None) -> FinalReport:
    """The complete workflow: all agents, then the validated final report."""
    results = analyze_resume(resume_text, job_description)
    draft = generate_feedback(results, resume_text)
    return build_final_report(results, draft, resume_text)