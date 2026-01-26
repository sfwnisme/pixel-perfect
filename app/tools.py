"""Custom tools for the migration agents."""

import subprocess


def run_shell_command(command: str) -> str:
    """Execute a shell command and return the output.
    
    Args:
        command: The shell command to execute.
        
    Returns:
        The stdout from the command, or an error message if it fails.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error running command: {e.stderr}"
