"""Configuration management for Pixel-Perfect CLI."""

import json
import os
from pathlib import Path
from typing import Optional

# Config file location
CONFIG_DIR = Path.home() / ".pixel-perfect"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Supported providers and their env var names
SUPPORTED_PROVIDERS = {
    "mistral": {
        "env_var": "MISTRAL_API_KEYS",
        "model_class": "agno.models.mistral.MistralChat",
        "default_model": "mistral-large-latest",
    },
    "openai": {
        "env_var": "OPENAI_API_KEY",
        "model_class": "agno.models.openai.OpenAIResponses",
        "default_model": "gpt-4o",
    },
    "anthropic": {
        "env_var": "ANTHROPIC_API_KEY",
        "model_class": "agno.models.anthropic.Claude",
        "default_model": "claude-sonnet-4-5",
    },
    "google": {
        "env_var": "GOOGLE_API_KEY",
        "model_class": "agno.models.google.Gemini",
        "default_model": "gemini-2.0-flash",
    },
    "groq": {
        "env_var": "GROQ_API_KEY",
        "model_class": "agno.models.groq.Groq",
        "default_model": "llama-3.3-70b-versatile",
    },
    "deepseek": {
        "env_var": "DEEPSEEK_API_KEY",
        "model_class": "agno.models.deepseek.DeepSeek",
        "default_model": "deepseek-chat",
    },
}


def _ensure_config_dir():
    """Ensure config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _load_config() -> dict:
    """Load configuration from file."""
    _ensure_config_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def _save_config(config: dict):
    """Save configuration to file."""
    _ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_provider() -> str:
    """Get the configured provider (default: mistral)."""
    config = _load_config()
    return config.get("provider", "mistral")


def set_provider(provider: str) -> bool:
    """Set the AI provider."""
    if provider not in SUPPORTED_PROVIDERS:
        return False
    config = _load_config()
    config["provider"] = provider
    _save_config(config)
    return True


def get_api_keys(provider: Optional[str] = None) -> list[str]:
    """Get API keys for the specified or current provider."""
    provider = provider or get_provider()
    config = _load_config()
    keys = config.get("api_keys", {}).get(provider, [])
    
    # Also check env var
    if not keys and provider in SUPPORTED_PROVIDERS:
        env_var = SUPPORTED_PROVIDERS[provider]["env_var"]
        env_keys = os.getenv(env_var, "")
        if env_keys:
            keys = [k.strip() for k in env_keys.split(",") if k.strip()]
    
    return keys


def add_api_key(key: str, provider: Optional[str] = None) -> bool:
    """Add one or more API keys for the specified or current provider."""
    provider = provider or get_provider()
    if provider not in SUPPORTED_PROVIDERS:
        return False
    
    config = _load_config()
    if "api_keys" not in config:
        config["api_keys"] = {}
    if provider not in config["api_keys"]:
        config["api_keys"][provider] = []
    
    # Handle comma-separated keys
    keys_to_add = [k.strip() for k in key.split(",") if k.strip()]
    
    added = False
    for k in keys_to_add:
        # Don't add duplicates
        if k not in config["api_keys"][provider]:
            config["api_keys"][provider].append(k)
            added = True
    
    if added:
        _save_config(config)
    return True


def clear_api_keys(provider: Optional[str] = None):
    """Clear all API keys for a provider."""
    provider = provider or get_provider()
    config = _load_config()
    if "api_keys" in config and provider in config["api_keys"]:
        config["api_keys"][provider] = []
        _save_config(config)


def get_model(provider: Optional[str] = None) -> str:
    """Get the model ID for the specified or current provider."""
    provider = provider or get_provider()
    config = _load_config()
    custom_model = config.get("models", {}).get(provider)
    if custom_model:
        return custom_model
    return SUPPORTED_PROVIDERS.get(provider, {}).get("default_model", "")


def set_model(model: str, provider: Optional[str] = None):
    """Set a custom model for the provider."""
    provider = provider or get_provider()
    config = _load_config()
    if "models" not in config:
        config["models"] = {}
    config["models"][provider] = model
    _save_config(config)


def show_config() -> dict:
    """Get the full configuration for display."""
    config = _load_config()
    provider = config.get("provider", "mistral")
    
    # Mask API keys for display
    masked_keys = {}
    for p, keys in config.get("api_keys", {}).items():
        masked_keys[p] = [f"{k[:8]}...{k[-4:]}" if len(k) > 12 else "***" for k in keys]
    
    return {
        "provider": provider,
        "model": get_model(provider),
        "api_keys": masked_keys,
        "config_file": str(CONFIG_FILE),
    }
