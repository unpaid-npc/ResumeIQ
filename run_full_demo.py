"""Runs the complete workflow on the synthetic resume.

    python run_full_demo.py            -> with a job description (5 API requests)
    python run_full_demo.py --no-job   -> without one (4 API requests)
"""
import sys

from backend.schemas import OutputValidationError
from run_match_demo import SAMPLE_JOB_DESCRIPTION
from run_parser_demo import SAMPLE_RESUME
from services.analysis_service import AnalysisError
from services.llm_config import ConfigError
from services.report_service import run_full_analysis


def show_list(title: str, items: list[str]) -> None:
    print(f"\n=== {title} ===")
    for item in items:
        print(f"- {item}")


def main() -> None:
    job = None if "--no-job" in sys.argv else SAMPLE_JOB_DESCRIPTION
    try:
        report = run_full_analysis(SAMPLE_RESUME, job)
    except (ConfigError, OutputValidationError, AnalysisError) as exc:
        print("Problem:", exc)
        return

    print("\n=== EXECUTIVE SUMMARY ===")
    print(report.executive_summary)

    print("\n=== SKILLS ===")
    for s in report.skills.skills:
        print(f"{s.skill:<14} {s.category:<20} {s.status}")

    print("\n=== SCORES (0-10) ===")
    print(", ".join(f"{k}={v}" for k, v in report.evaluation.scores.model_dump().items()))

    show_list("STRENGTHS", report.strengths)
    show_list("WEAKNESSES", report.weaknesses)

    print("\n=== JOB MATCH ===")
    if report.job_match is None:
        print("Skipped (no job description).")
    else:
        for m in report.job_match.matches:
            print(f"[{m.status:<11}] {m.requirement}")

    show_list("RECOMMENDATIONS", report.recommendations)

    print("\n=== BULLET REWRITES (faithful ones only) ===")
    if not report.bullet_rewrites:
        print("(none passed the faithfulness check)")
    for r in report.bullet_rewrites:
        print(f"BEFORE: {r.original}")
        print(f"AFTER : {r.improved}\n")

    show_list("NEXT STEPS", report.next_steps)


if __name__ == "__main__":
    main()