"""Runs the agents one after another and returns validated results."""
from dataclasses import dataclass

from crewai import Crew, Process

from agents.resume_evaluator import create_evaluator_agent
from agents.resume_parser import create_resume_parser_agent
from agents.skills_analyst import create_skills_agent
from backend.schemas import (
    OutputValidationError,
    ParsedResume,
    ResumeEvaluation,
    SkillsAnalysis,
    parse_model_output,
)
from services.llm_config import get_llm
from tasks.resume_tasks import (
    create_evaluation_task,
    create_parse_task,
    create_skills_task,
)

MAX_ATTEMPTS = 2  # first try plus one retry if the model returns broken output


class AnalysisError(Exception):
    """Raised when the analysis cannot start (for example, empty input)."""


@dataclass
class AnalysisResults:
    parsed: ParsedResume
    skills: SkillsAnalysis
    evaluation: ResumeEvaluation


def _run_crew(agents: list, tasks: list) -> str:
    """Run agents one after another (sequential) and return the final raw text."""
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.raw


def _run_stage(model_class, make_agent_and_task):
    """Run one agent, validate its answer, retry once if the answer is broken."""
    last_error = None
    for _ in range(MAX_ATTEMPTS):
        agent, task = make_agent_and_task()
        raw = _run_crew([agent], [task])
        try:
            return parse_model_output(model_class, raw)
        except OutputValidationError as exc:
            last_error = exc
    raise last_error


def _require_text(resume_text: str) -> None:
    if not resume_text or not resume_text.strip():
        raise AnalysisError("Resume text is empty.")


def parse_resume(resume_text: str) -> ParsedResume:
    _require_text(resume_text)
    llm = get_llm()

    def make():
        agent = create_resume_parser_agent(llm)
        return agent, create_parse_task(agent, resume_text)

    return _run_stage(ParsedResume, make)


def analyze_skills(parsed: ParsedResume, resume_text: str) -> SkillsAnalysis:
    llm = get_llm()

    def make():
        agent = create_skills_agent(llm)
        return agent, create_skills_task(agent, parsed, resume_text)

    return _run_stage(SkillsAnalysis, make)


def evaluate_resume(
    parsed: ParsedResume, skills: SkillsAnalysis, resume_text: str
) -> ResumeEvaluation:
    llm = get_llm()

    def make():
        agent = create_evaluator_agent(llm)
        return agent, create_evaluation_task(agent, parsed, skills, resume_text)

    return _run_stage(ResumeEvaluation, make)


def analyze_resume(resume_text: str) -> AnalysisResults:
    """Parser -> Skills Analyst -> Evaluator. Each output feeds the next agent."""
    _require_text(resume_text)
    parsed = parse_resume(resume_text)
    skills = analyze_skills(parsed, resume_text)
    evaluation = evaluate_resume(parsed, skills, resume_text)
    return AnalysisResults(parsed=parsed, skills=skills, evaluation=evaluation)