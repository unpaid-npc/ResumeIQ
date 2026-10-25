"""Sends a synthetic (made-up) resume to the Resume Parser Agent. Uses 1 API request."""
from backend.schemas import OutputValidationError
from services.analysis_service import parse_resume
from services.llm_config import ConfigError

SAMPLE_RESUME = """
Aarav Mehta
Pune, India | aarav.mehta@example.com | github.com/aarav-demo

EDUCATION
B.Sc. Computer Science, Demo University, 2021 - 2024, CGPA 8.2

EXPERIENCE
Data Analyst Intern, Sample Analytics Pvt Ltd (Jun 2023 - Aug 2023)
- Cleaned sales data using Python and Pandas
- Built a weekly sales report in Excel for the team

PROJECTS
Sales Dashboard
- Built an interactive dashboard using Python, Plotly and Streamlit
- Analyzed 10,000 sales records to find top-selling products

CERTIFICATIONS
Google Data Analytics Certificate, Coursera, 2023

SKILLS
Python, SQL, Pandas, Plotly, Streamlit, Tableau
Communication, Teamwork
"""


def main() -> None:
    try:
        result = parse_resume(SAMPLE_RESUME)
    except (ConfigError, OutputValidationError) as exc:
        print("Problem:", exc)
        return
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()