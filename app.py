"""ResumeIQ entry point. Day 1: only checks that the setup works."""
import sys

from dotenv import load_dotenv


def main() -> None:
    load_dotenv()
    print("ResumeIQ setup OK")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Running from: {sys.prefix}")


if __name__ == "__main__":
    main()