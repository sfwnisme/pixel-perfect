"""Developer agent for executing the migration."""

from agno.agent import Agent
from agno.models.mistral import MistralChat
from agno.tools.local_file_system import LocalFileSystemTools

from app.config import key_manager


def create_developer_agent(base_dir: str = ".") -> Agent:
    """Create a Developer agent for executing migrations.
    
    Args:
        base_dir: Base directory for file system operations.
        
    Returns:
        Configured Developer agent.
    """
    # Set up file tools
    try:
        file_tools = LocalFileSystemTools(target_directory=base_dir)
    except TypeError:
        # Fallback for different library versions
        file_tools = LocalFileSystemTools()

    model = MistralChat(
        id="mistral-large-latest",
        api_key=key_manager.get_next_key(),
    )

    return Agent(
        name="Developer",
        role="Execute the migration by writing Nuxt.js files",
        model=model,
        tools=[file_tools],
        instructions="Implement the migration plan by converting files to Nuxt.js.",
    )
