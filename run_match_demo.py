"""Runs all four agents with a synthetic job description. Uses 4 API requests."""
from backend.schemas import OutputValidationError
from run_parser_demo import SAMPLE_RESUME
from services.analysis_service import AnalysisError, analyze_resume
from services.llm_config import ConfigError

SAMPLE_JOB_DESCRIPTION = """
Junior Data Analyst - Example Corp (made-up job for testing)

Requirements:
- Strong Python and SQL skills
- Experience building dashboards in Tableau or Power BI
- Experience with machine learning models
- 3+ years of professional experience in data analysis
- Clear communication with non-technical teams
"""


def main() -> None:
    try:
        results = analyze_resume(SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION)
    except (ConfigError, OutputValidationError, AnalysisError) as exc:
        print("Problem:", exc)
        return

    match = results.job_match
    print("\n=== JOB MATCH ===")
    for m in match.matches:
        print(f"[{m.status:<11}] {m.requirement}")
        if m.evidence:
            print(f"               evidence: {m.evidence}")
    print("\nEmphasize:", ", ".join(match.experience_to_emphasize) or "-")
    print("Develop:  ", ", ".join(match.skills_to_develop) or "-")


if __name__ == "__main__":
    main()