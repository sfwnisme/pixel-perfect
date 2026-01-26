"""Scenario test for Next.js to Nuxt.js migration."""

import os
import shutil
import pytest
import scenario
from dotenv import load_dotenv

from app.team import get_migration_team

load_dotenv()

# Configure default model for scenario
scenario.configure(default_model="gpt-4o")


class MigrationTeamAdapter(scenario.AgentAdapter):
    """Adapter for the migration team to work with Scenario."""

    def __init__(self):
        self.team = get_migration_team()

    async def call(self, input: scenario.AgentInput) -> scenario.AgentReturnTypes:
        """Run the team with the user input."""
        response = self.team.run(
            input.last_new_user_message_str(),
            session_id=input.thread_id
        )
        return response.content


@pytest.mark.asyncio
async def test_migration_scenario():
    """Test that the migration team can successfully migrate a Next.js app."""
    # Setup paths
    repo_path = "tests/fixtures/next_app"
    output_path = "tests/fixtures/output_nuxt"
    
    # Clean output
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # Run Scenario
    result = await scenario.run(
        name="Next.js to Nuxt.js Migration",
        description="Migrate a simple Next.js app to Nuxt.js",
        agents=[
            MigrationTeamAdapter(),
            scenario.UserSimulatorAgent(),
            scenario.JudgeAgent(criteria=[
                "Agent should analyze the provided path",
                "Agent should generate Nuxt.js files in the output directory",
                "Agent should confirm the migration is complete",
                "The output directory should contain 'app.vue' or 'pages/index.vue'",
            ])
        ],
        script=[
            scenario.user(f"Please migrate the Next.js app at '{repo_path}' to '{output_path}'."),
            scenario.agent(),
            scenario.judge()
        ]
    )

    # Verify files exist
    assert result.success
    
    # Additional assertion for side effects
    assert os.path.exists(os.path.join(output_path, "pages", "index.vue")) or \
           os.path.exists(os.path.join(output_path, "app.vue"))
