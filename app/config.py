"""Configuration and environment management for Pixel-Perfect."""

import os
from typing import Optional

from dotenv import load_dotenv
from agno.db.sqlite import SqliteDb

# Load environment variables
load_dotenv()


class APIKeyManager:
    """Round-robin API key manager with CLI config support."""

    def __init__(self, provider: str = None):
        """
        Initialize the key manager.
        
        Args:
            provider: The provider to manage keys for. If None, uses the globally configured provider.
        """
        from app import cli_config
        
        self.provider = provider or cli_config.get_provider()
        
        # First try CLI config
        self.keys = cli_config.get_api_keys(self.provider)
        
        # Fallback to environment variables
        if not self.keys:
            provider_config = cli_config.SUPPORTED_PROVIDERS.get(self.provider, {})
            env_var = provider_config.get("env_var", "")
            if env_var:
                env_keys = os.getenv(env_var, "")
                if env_keys:
                    self.keys = [k.strip() for k in env_keys.split(",") if k.strip()]
        
        if not self.keys:
            # We don't print warning here anymore to avoid noise when accessing auxiliary keys
            pass
        
        self.index = 0

    def get_next_key(self) -> Optional[str]:
        """Get the next API key in round-robin fashion."""
        if not self.keys:
            return None
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

    def get_key(self, provider: str) -> Optional[str]:
        """Get a key for a specific provider (without switching the main provider context)."""
        # Create a temporary manager for the requested provider
        temp_manager = APIKeyManager(provider)
        return temp_manager.get_next_key()


def get_model():
    """Get the configured model instance based on CLI config."""
    from app import cli_config
    
    provider = cli_config.get_provider()
    model_id = cli_config.get_model(provider)
    key_manager = APIKeyManager(provider)
    api_key = key_manager.get_next_key()
    
    if provider == "mistral":
        from agno.models.mistral import MistralChat
        return MistralChat(id=model_id, api_key=api_key)
    elif provider == "openai":
        from agno.models.openai import OpenAIResponses
        return OpenAIResponses(id=model_id, api_key=api_key)
    elif provider == "anthropic":
        from agno.models.anthropic import Claude
        return Claude(id=model_id, api_key=api_key)
    elif provider == "google":
        from agno.models.google import Gemini
        return Gemini(id=model_id, api_key=api_key)
    elif provider == "groq":
        from agno.models.groq import Groq
        return Groq(id=model_id, api_key=api_key)
    elif provider == "deepseek":
        from agno.models.deepseek import DeepSeek
        return DeepSeek(id=model_id, api_key=api_key)
    else:
        # Default fallback to Mistral
        from agno.models.mistral import MistralChat
        return MistralChat(id="mistral-large-latest", api_key=api_key)


# Legacy support - create key manager for default provider
key_manager = APIKeyManager()


def get_database(db_file: str = "tmp/agent_storage.db") -> SqliteDb:
    """Get the database instance for agent storage."""
    return SqliteDb(db_file=db_file)
