"""Team orchestration for the migration agents."""

import langwatch
from agno.models.mistral import MistralChat
from agno.team.team import Team

from app.config import key_manager, get_database
from app.agents import (
    create_analyzer_agent,
    create_architect_agent,
    create_developer_agent,
)


def get_migration_team(base_dir: str = ".") -> Team:
    """Create and configure the migration team.
    
    Args:
        base_dir: Base directory for file system operations.
        
    Returns:
        Configured Team with Analyzer, Architect, and Developer agents.
    """
    # Fetch prompt from LangWatch
    try:
        prompt_data = langwatch.prompts.get("pixel_perfect_migration")
        system_prompt = ""
        for msg in prompt_data.messages:
            # Handle both object and dict access for robustness
            if hasattr(msg, "role"):
                role = msg.role
                content = msg.content
            else:
                role = msg.get("role")
                content = msg.get("content")

            if role == "system":
                system_prompt = content
    except Exception as e:
        # Fallback if prompt fetching fails
        print(f"Warning: Failed to fetch prompt from LangWatch: {e}")
        system_prompt = "You are a migration agent expert specialized in Next.js to Nuxt.js."

    # Create agents
    analyzer = create_analyzer_agent(base_dir)
    architect = create_architect_agent()
    developer = create_developer_agent(base_dir)

    # Get model for team orchestration
    model = MistralChat(
        id="mistral-large-latest",
        api_key=key_manager.get_next_key(),
    )

    # Storage for sessions
    db = get_database()

    # Team orchestration
    return Team(
        members=[analyzer, architect, developer],
        model=model,
        instructions=system_prompt,
        db=db,
        num_history_messages=10,
        markdown=True,
    )


# Alias for backward compatibility
get_migration_agent = get_migration_team
