"""CLI entry point for the Pixel-Perfect Migration Agent using cli2."""

import asyncio
import os
import sys

import cli2

# Ensure app package is importable when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.team import get_migration_team, get_migration_team_with_mcp
from app.tools import run_shell_command


# Create CLI group
cli = cli2.Group(doc="""
Pixel-Perfect: Next.js to Nuxt.js Migration Agent

Automatically migrate your Next.js applications to Nuxt.js with AI-powered
analysis, planning, and code generation.

Now with Nuxt MCP integration for accurate, up-to-date Nuxt.js patterns!
""")


async def _migrate_with_mcp(source_path: str, output_dir: str):
    """Run migration with Nuxt MCP for accurate code generation."""
    team, nuxt_mcp = await get_migration_team_with_mcp(base_dir=os.getcwd())

    prompt = f"""
    I want to migrate the Next.js application located at '{source_path}' to a Nuxt.js application at '{output_dir}'.
    
    Please follow this process:
    1. Analyzer: List and analyze the files in '{source_path}'.
    2. Architect: Create a MigrationPlan for converting to Nuxt.js in '{output_dir}'.
    3. Developer: Execute the plan and write the new files.
       Use the Nuxt MCP tools to look up correct patterns and best practices.
    """

    try:
        await team.aprint_response(prompt, stream=True)
    finally:
        await nuxt_mcp.close()


@cli.cmd
def migrate(repo: str, output: str, mcp: bool = True):
    """
    Migrate a Next.js application to Nuxt.js.

    :param repo: GitHub repository URL or local path to the Next.js app
    :param output: Output directory for the generated Nuxt.js app
    :param mcp: Use Nuxt MCP for accurate code generation (default: True)
    """
    # Ensure output directory exists
    output_dir = os.path.abspath(output)
    os.makedirs(output_dir, exist_ok=True)

    source_path = os.path.abspath(repo)
    if repo.startswith("http"):
        repo_name = repo.split("/")[-1].replace(".git", "")
        temp_dir = f"tmp/clones/{repo_name}"
        print(f"Cloning {repo} to {temp_dir}...")
        run_shell_command(f"git clone {repo} {temp_dir}")
        source_path = os.path.abspath(temp_dir)

    print(f"Starting migration from {source_path} to {output_dir}...")

    if mcp:
        print("Using Nuxt MCP for accurate code generation...")
        asyncio.run(_migrate_with_mcp(source_path, output_dir))
    else:
        # Sync version without MCP
        team = get_migration_team(base_dir=os.getcwd())
        prompt = f"""
        I want to migrate the Next.js application located at '{source_path}' to a Nuxt.js application at '{output_dir}'.
        
        Please follow this process:
        1. Analyzer: List and analyze the files in '{source_path}'.
        2. Architect: Create a MigrationPlan for converting to Nuxt.js in '{output_dir}'.
        3. Developer: Execute the plan and write the new files.
        """
        team.print_response(prompt, stream=True)


@cli.cmd
def analyze(repo: str):
    """
    Analyze a Next.js project structure without migrating.

    :param repo: Path to the Next.js application to analyze
    """
    from app.agents import create_analyzer_agent

    source_path = os.path.abspath(repo)
    if not os.path.exists(source_path):
        print(f"Error: Path '{source_path}' does not exist")
        return

    print(f"Analyzing {source_path}...")
    
    analyzer = create_analyzer_agent(base_dir=source_path)
    analyzer.print_response(
        f"Analyze the Next.js project at '{source_path}'. List all files, identify the framework version, dependencies, and key architectural patterns.",
        stream=True
    )


@cli.cmd
def version():
    """Show the version of pixel-perfect."""
    print("pixel-perfect v0.1.0")
    print("  - Nuxt MCP integration: enabled")


def main():
    """Entry point for the CLI."""
    cli.entry_point()


if __name__ == "__main__":
    main()