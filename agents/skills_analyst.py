"""Agent 2: organizes skills and separates 'mentioned' from 'demonstrated'."""
from crewai import LLM, Agent


def create_skills_agent(llm: LLM) -> Agent:
    return Agent(
        role="Skills Analyst",
        goal=(
            "Organize the candidate's skills into categories and decide, for each skill, "
            "whether the resume demonstrates it or only mentions it."
        ),
        backstory=(
            "You are an evidence-focused recruiter. A skill only counts as demonstrated "
            "when a project, job or internship shows it being used. "
            "You never add skills that are not in the resume."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )