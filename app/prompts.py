"""Prompt management for Pixel-Perfect agents.

This module handles loading system prompts, prioritizing robust local defaults
and optionally fetching dynamic updates from LangWatch if configured.
"""

import os
import logging
from typing import Optional

# Safe default prompt embedded in the binary
DEFAULT_MIGRATION_SYSTEM_PROMPT = """You are a migration agent expert specialized in converting Next.js structure to Nuxt.js 4.

Your Goal:
Orchestrate a team of agents to analyze a Next.js codebase and rebuild it as a pixel-perfect Nuxt.js 4 application.

Key Principles:
1. **Pixel-Perfect Fidelity**: The migrated app MUST look exactly like the original. Preserve all CSS, Tailwind config, fonts, and assets.
2. **Nuxt 4 / VS Code Best Practices**: Use the latest `nuxi` scaffolding, auto-imports, and TypeScript features.
3. **Safety**: Do not overwrite existing non-empty directories without warning (handled by CLI, but keep in mind).

Process:
1. **Analyze**: Understand the source structure (App Router vs Pages Router).
2. **Plan**: Create a detailed step-by-step implementation plan.
3. **Execute**: Use the Developer agent to scaffold and write code.
"""

def get_system_prompt() -> str:
    """
    Fetch the system prompt.
    
    Strategy:
    1. Check if LANGWATCH_API_KEY is present.
    2. If yes, try to fetch 'pixel_perfect_migration' from LangWatch.
    3. If no key, or fetch fails, return DEFAULT_MIGRATION_SYSTEM_PROMPT.
    """
    api_key = os.getenv("LANGWATCH_API_KEY")
    if not api_key:
        return DEFAULT_MIGRATION_SYSTEM_PROMPT

    try:
        import langwatch
        prompt_data = langwatch.prompts.get("pixel_perfect_migration")
        
        # Extract system content from messages
        for msg in prompt_data.messages:
            # Handle object or dict access depending on SDK version
            role = getattr(msg, "role", None) or msg.get("role")
            content = getattr(msg, "content", None) or msg.get("content")
            
            if role == "system":
                return content
                
    except Exception as e:
        # Log warning but don't crash
        logging.warning(f"Failed to fetch prompt from LangWatch: {e}. Using default.")
        
    return DEFAULT_MIGRATION_SYSTEM_PROMPT
