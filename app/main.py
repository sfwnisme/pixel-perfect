"""CLI entry point for the Pixel-Perfect Migration Agent using cli2."""

import asyncio
import os
import sys

import cli2

# Ensure app package is importable when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.team import get_migration_team, get_migration_team_with_mcp
from app.tools import run_shell_command
from app import cli_config


# Create CLI group
cli = cli2.Group(doc="""
Pixel-Perfect: Next.js to Nuxt.js Migration Agent

Automatically migrate your Next.js applications to Nuxt.js with AI-powered
analysis, planning, and code generation.

Commands:
  migrate        - Migrate a Next.js app to Nuxt.js
  analyze        - Analyze a Next.js project
  config-show    - Show current configuration
  config-provider - Set AI provider
  config-key     - Add API key
  config-model   - Set model
  version        - Show version info
""")


# --- Config Commands ---

@cli.cmd(name="config-show")
def config_show():
    """Show current configuration."""
    cfg = cli_config.show_config()
    print(f"Provider: {cfg['provider']}")
    print(f"Model: {cfg['model']}")
    print(f"Config file: {cfg['config_file']}")
    print()
    print("API Keys:")
    for provider, keys in cfg['api_keys'].items():
        if keys:
            print(f"  {provider}: {', '.join(keys)}")
    if not any(cfg['api_keys'].values()):
        print("  (none configured)")
    print()
    print("Supported providers:", ", ".join(cli_config.SUPPORTED_PROVIDERS.keys()))


@cli.cmd(name="config-provider")
def config_provider(provider: str):
    """
    Set the AI provider to use.

    :param provider: Provider name (mistral, openai, anthropic, google, groq, deepseek)
    """
    if cli_config.set_provider(provider):
        print(f"✓ Provider set to: {provider}")
        print(f"  Default model: {cli_config.get_model(provider)}")
    else:
        print(f"✗ Unknown provider: {provider}")
        print(f"  Supported: {', '.join(cli_config.SUPPORTED_PROVIDERS.keys())}")


@cli.cmd(name="config-key")
def config_key(key: str, provider: str = None):
    """
    Add API key(s) for a provider. Supports comma-separated keys for load balancing.

    :param key: The API key(s) to add (can be comma-separated)
    :param provider: Provider name (defaults to current provider)
    """
    provider = provider or cli_config.get_provider()
    if cli_config.add_api_key(key, provider):
        keys = [k.strip() for k in key.split(",") if k.strip()]
        if len(keys) > 1:
            print(f"✓ Added {len(keys)} keys for {provider}")
        else:
            masked = f"{keys[0][:8]}...{keys[0][-4:]}" if len(keys[0]) > 12 else "***"
            print(f"✓ Added key for {provider}: {masked}")
    else:
        print(f"✗ Failed to add key for {provider}")


@cli.cmd(name="config-clear")
def config_clear(provider: str = None):
    """
    Clear all API keys for a provider.

    :param provider: Provider name (defaults to current provider)
    """
    provider = provider or cli_config.get_provider()
    cli_config.clear_api_keys(provider)
    print(f"✓ Cleared all keys for {provider}")


@cli.cmd(name="config-model")
def config_model(model: str, provider: str = None):
    """
    Set the model to use for a provider.

    :param model: Model ID (e.g., gpt-4o, claude-sonnet-4-5)
    :param provider: Provider name (defaults to current provider)
    """
    provider = provider or cli_config.get_provider()
    cli_config.set_model(model, provider)
    print(f"✓ Model for {provider} set to: {model}")


# --- Migration Commands ---

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
        # Use interactive CLI app for multi-turn conversation
        await team.acli_app(input=prompt, stream=True)
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
    print(f"Using provider: {cli_config.get_provider()}")

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
        # Use interactive CLI app for multi-turn conversation
        team.cli_app(input=prompt, stream=True)


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
    print(f"  Provider: {cli_config.get_provider()}")
    print(f"  Model: {cli_config.get_model()}")
    print("  Nuxt MCP: enabled")


def main():
    """Entry point for the CLI."""
    cli.entry_point()


if __name__ == "__main__":
    main()