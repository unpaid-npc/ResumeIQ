"""Runs the agents and returns validated results."""
from crewai import Crew, Process

from agents.resume_parser import create_resume_parser_agent
from backend.schemas import ParsedResume, parse_model_output
from services.llm_config import get_llm
from tasks.resume_tasks import create_parse_task


class AnalysisError(Exception):
    """Raised when the analysis cannot start (for example, empty input)."""


def _run_crew(agents: list, tasks: list) -> str:
    """Run agents one after another (sequential) and return the final raw text."""
    crew = Crew(agents=agents, tasks=tasks, process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return result.raw


def parse_resume(resume_text: str) -> ParsedResume:
    if not resume_text or not resume_text.strip():
        raise AnalysisError("Resume text is empty.")
    llm = get_llm()
    agent = create_resume_parser_agent(llm)
    task = create_parse_task(agent, resume_text)
    raw = _run_crew([agent], [task])
    return parse_model_output(ParsedResume, raw)