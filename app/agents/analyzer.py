"""Analyzer agent for inspecting Next.js project structure."""

from agno.agent import Agent
from agno.models.mistral import MistralChat
from agno.tools.local_file_system import LocalFileSystemTools

from app.config import key_manager
from app.tools import run_shell_command


def create_analyzer_agent(base_dir: str = ".") -> Agent:
    """Create an Analyzer agent for Next.js project analysis.
    
    Args:
        base_dir: Base directory for file system operations.
        
    Returns:
        Configured Analyzer agent.
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
        name="Analyzer",
        role="Analyze Next.js project structure and dependencies",
        model=model,
        tools=[file_tools, run_shell_command],
        instructions="Analyze the source directory and provide a detailed structure.",
    )
