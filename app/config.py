"""Configuration and environment management for Pixel-Perfect."""

import os
from typing import Optional

from dotenv import load_dotenv
from agno.db.sqlite import SqliteDb

# Load environment variables
load_dotenv()


class MistralKeyManager:
    """Round-robin API key manager for Mistral load balancing."""

    def __init__(self):
        # Try comma-separated keys first (recommended format)
        keys_str = os.getenv("MISTRAL_API_KEYS")
        if keys_str:
            self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        else:
            # Fallback to individual key variables
            self.keys = [
                os.getenv("MISTRAL_API_KEY_1"),
                os.getenv("MISTRAL_API_KEY_2"),
            ]
            # Filter out None keys
            self.keys = [k for k in self.keys if k]
            
            # Final fallback to single MISTRAL_API_KEY
            if not self.keys:
                single_key = os.getenv("MISTRAL_API_KEY")
                if single_key:
                    self.keys = [single_key]
                else:
                    print("Warning: No Mistral API keys found in environment variables.")

        self.index = 0

    def get_next_key(self) -> Optional[str]:
        """Get the next API key in round-robin fashion."""
        if not self.keys:
            return None
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key


# Singleton instance for key management
key_manager = MistralKeyManager()


def get_database(db_file: str = "tmp/agent_storage.db") -> SqliteDb:
    """Get the database instance for agent storage."""
    return SqliteDb(db_file=db_file)
