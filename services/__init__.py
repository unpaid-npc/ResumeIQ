"""Privacy settings: stop CrewAI from sending traces or telemetry anywhere.

This file runs before any other services module, so the settings are in place
before CrewAI starts.
"""
import os

os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("CREWAI_DISABLE_TRACKING", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")