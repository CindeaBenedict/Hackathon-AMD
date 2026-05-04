"""Process-wide singletons (avoid import cycles between routers and main)."""

from app.services.agent import ProbePilotAgent

agent = ProbePilotAgent()
