"""Agent 1: reads resume text and extracts structured facts."""
from crewai import LLM, Agent


def create_resume_parser_agent(llm: LLM) -> Agent:
    return Agent(
        role="Resume Parser",
        goal=(
            "Extract facts from resume text into a structured format, "
            "using only information that is actually written in the resume."
        ),
        backstory=(
            "You are a careful data-entry specialist. You copy what the resume says "
            "and never guess. If something is missing, you leave it empty."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )