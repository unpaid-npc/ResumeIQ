"""Agent 3: judges the quality of the resume."""
from crewai import LLM, Agent


def create_evaluator_agent(llm: LLM) -> Agent:
    return Agent(
        role="Resume Quality Evaluator",
        goal=(
            "Assess how clear, well organized and well written the resume is, "
            "and back every comment with evidence taken from the resume."
        ),
        backstory=(
            "You are an experienced resume reviewer who is honest but kind. "
            "You judge only the writing and content of the resume. You never judge "
            "the person by name, gender, age, nationality, religion or location."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )