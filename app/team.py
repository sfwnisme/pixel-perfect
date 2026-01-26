"""Team orchestration for the migration agents."""


from agno.team.team import Team
from agno.tools.mcp import MCPTools

from app.config import get_database, get_model
from app.agents import (
    create_analyzer_agent,
    create_architect_agent,
    create_developer_agent,
)
from app.agents.developer import create_developer_agent_with_mcp


from app.prompts import get_system_prompt


def get_migration_team(base_dir: str = ".", session_id: str = None) -> Team:
    """Create and configure the migration team (sync version).
    
    Args:
        base_dir: Base directory for file system operations.
        session_id: Optional session ID to resume.
        
    Returns:
        Configured Team with Analyzer, Architect, and Developer agents.
    """
    system_prompt = get_system_prompt()

    # Create agents
    analyzer = create_analyzer_agent(base_dir)
    architect = create_architect_agent()
    developer = create_developer_agent(base_dir)

    # Get model for team orchestration
    model = get_model()

    # Storage for sessions
    db = get_database()

    # Team orchestration
    return Team(
        session_id=session_id,
        members=[analyzer, architect, developer],
        model=model,
        instructions=system_prompt,
        db=db,
        num_history_messages=10,
        add_history_to_context=True,
        markdown=True,
    )


async def get_migration_team_with_mcp(base_dir: str = ".", session_id: str = None) -> tuple[Team, MCPTools]:
    """Create migration team with Nuxt MCP for accurate code generation.
    
    Args:
        base_dir: Base directory for file system operations.
        session_id: Optional session ID to resume.
        
    Returns:
        Tuple of (Team, MCPTools) - MCPTools must be closed when done.
    """
    system_prompt = get_system_prompt()

    # Create agents (developer with MCP)
    analyzer = create_analyzer_agent(base_dir)
    architect = create_architect_agent()
    developer, nuxt_mcp = await create_developer_agent_with_mcp(base_dir)

    # Get model for team orchestration
    model = get_model()

    # Storage for sessions
    db = get_database()

    # Team orchestration
    team = Team(
        session_id=session_id,
        members=[analyzer, architect, developer],
        model=model,
        instructions=system_prompt,
        db=db,
        num_history_messages=10,
        add_history_to_context=True,
        markdown=True,
    )

    return team, nuxt_mcp


# Alias for backward compatibility
get_migration_agent = get_migration_team
