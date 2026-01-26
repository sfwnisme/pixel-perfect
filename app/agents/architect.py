"""Architect agent for designing the Nuxt.js migration plan."""

from agno.agent import Agent

from app.config import get_model
from app.schemas import MigrationPlan


def create_architect_agent() -> Agent:
    """Create an Architect agent for migration planning.
    
    Returns:
        Configured Architect agent with MigrationPlan output schema.
    """
    model = get_model()

    return Agent(
        name="Architect",
        role="Design the Nuxt.js migration plan",
        model=model,
        output_schema=MigrationPlan,
        instructions="Based on the analysis, create a comprehensive MigrationPlan.",
    )
