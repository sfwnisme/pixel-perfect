"""Pydantic models for structured agent outputs."""

from typing import List

from pydantic import BaseModel, Field


class FileMigration(BaseModel):
    """Represents a single file migration from Next.js to Nuxt.js."""

    source_path: str = Field(..., description="Path to the original Next.js file")
    target_path: str = Field(..., description="Proposed path for the Nuxt.js equivalent")
    action: str = Field(..., description="Action to take: 'convert', 'copy', or 'create'")
    description: str = Field(..., description="Brief explanation of the conversion logic")


class MigrationPlan(BaseModel):
    """Complete migration plan from Next.js to Nuxt.js."""

    project_name: str = Field(..., description="Name of the project being migrated")
    summary: str = Field(..., description="High-level summary of the migration strategy")
    files_to_migrate: List[FileMigration] = Field(
        ..., description="List of specific file migrations"
    )
    config_changes: List[str] = Field(
        ..., description="Key changes needed in configuration files (nuxt.config.ts, etc.)"
    )
