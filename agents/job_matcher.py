"""Agent 4: compares the resume with a job description (optional step)."""
from crewai import LLM, Agent


def create_job_match_agent(llm: LLM) -> Agent:
    return Agent(
        role="Job Match Analyst",
        goal=(
            "Compare each requirement in a job description with the evidence in the resume, "
            "and report honestly what is supported, partly supported, or not shown."
        ),
        backstory=(
            "You are a fair hiring screener. You only count what the resume actually shows. "
            "You never invent qualifications, and you never advise a candidate to claim "
            "skills or experience they do not have."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )