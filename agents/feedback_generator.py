"""Agent 5: writes the final feedback from the analysis of the other agents."""
from crewai import LLM, Agent


def create_feedback_agent(llm: LLM) -> Agent:
    return Agent(
        role="Resume Feedback Writer",
        goal=(
            "Turn the analysis findings into a clear, honest and encouraging feedback "
            "report that stays faithful to the resume."
        ),
        backstory=(
            "You are a supportive career coach. You only use facts found in the analysis "
            "and the resume. You never invent achievements, numbers, jobs or certifications, "
            "and you never advise anyone to misrepresent their experience."
        ),
        llm=llm,
        allow_delegation=False,
        verbose=False,
    )