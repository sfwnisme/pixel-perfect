"""Analyzer agent for inspecting Next.js project structure."""

from agno.agent import Agent
from agno.tools.local_file_system import LocalFileSystemTools

from app.config import get_model
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

    model = get_model()

    return Agent(
        name="Analyzer",
        role="Analyze Next.js project structure and dependencies",
        model=model,
        tools=[file_tools, run_shell_command],
        instructions="""Analyze the source directory and provide a detailed structure.

IMPORTANT: Pay special attention to styling and UI assets.
1. Identify the styling framework (Tailwind, CSS Modules, Styled Components, etc.).
2. Locate the global CSS file and configuration (e.g., `tailwind.config.js`).
3. List all UI component libraries used (Shadcn, Radix, Material UI).
4. Identify public assets (images, fonts) and where they are used.

Report this clearly so the Developer agent can recreate the pixel-perfect UI.
""",
    )
