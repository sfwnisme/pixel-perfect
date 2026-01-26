"""Developer agent for executing the migration with Nuxt MCP support."""

from agno.agent import Agent
from agno.tools.local_file_system import LocalFileSystemTools
from agno.tools.mcp import MCPTools

from app.config import get_model


def create_developer_agent(base_dir: str = ".") -> Agent:
    """Create a Developer agent for executing migrations (sync version).
    
    Args:
        base_dir: Base directory for file system operations.
        
    Returns:
        Configured Developer agent.
    """
    # Set up file tools
    try:
        file_tools = LocalFileSystemTools(target_directory=base_dir)
    except TypeError:
        file_tools = LocalFileSystemTools()

    model = get_model()

    return Agent(
        name="Developer",
        role="Execute the migration by writing Nuxt.js files",
        model=model,
        tools=[file_tools],
        instructions="Implement the migration plan by converting files to Nuxt.js.",
    )


async def create_developer_agent_with_mcp(base_dir: str = ".") -> tuple[Agent, MCPTools]:
    """Create a Developer agent with Nuxt MCP for accurate code generation.
    
    Args:
        base_dir: Base directory for file system operations.
        
    Returns:
        Tuple of (Agent, MCPTools) - MCPTools must be closed when done.
    """
    # Connect to Nuxt MCP server for up-to-date Nuxt.js knowledge
    nuxt_mcp = MCPTools(
        url="https://nuxt.com/mcp",
        transport="streamable-http"
    )
    await nuxt_mcp.connect()

    # Set up file tools
    try:
        file_tools = LocalFileSystemTools(target_directory=base_dir)
    except TypeError:
        file_tools = LocalFileSystemTools()

    model = get_model()

    agent = Agent(
        name="Developer",
        role="Execute the migration by writing Nuxt.js files",
        model=model,
        tools=[file_tools, nuxt_mcp],
        instructions="""Implement the migration plan by converting files to Nuxt.js.

IMPORTANT: Use the Nuxt MCP tools to:
- Look up correct Nuxt.js 3 patterns and composables
- Verify component syntax and best practices
- Get accurate imports and module structures

Always generate idiomatic Nuxt.js 3 code with:
- <script setup> syntax
- defineProps/defineEmits for component APIs
- Proper Nuxt auto-imports (useFetch, useRoute, useState, etc.)
- Correct file conventions (pages/, components/, composables/)
""",
    )

    return agent, nuxt_mcp
