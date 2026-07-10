import subprocess

run_terminal_schema = {
    "type": "function",
    "function": {
        "name": "run_terminal",
        "description": (
            "Run a shell/terminal command and return its output. "
            "Use for things like 'npm install', 'git clone', 'python app.py', 'pip install X'. "
            "This is powerful — it can install packages, run scripts, and modify files."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The command to run, e.g. 'git clone <url>'."},
                "working_directory": {
                    "type": "string",
                    "description": "Directory to run the command in. Defaults to the agent's current directory."
                }
            },
            "required": ["command"]
        }
    }
}

# Commands you never want an LLM freely invoking, even accidentally.
# Extend this list as you find more danger zones.
BLOCKED_SUBSTRINGS = [
    "rm -rf /", "format ", "del /f /s /q", "shutdown", "mkfs",
    ":(){ :|:& };:",  # fork bomb
]

TIMEOUT_SECONDS = 60


def run_terminal(command, working_directory=None):
    lowered = command.lower()

    for blocked in BLOCKED_SUBSTRINGS:
        if blocked in lowered:
            return f"Blocked for safety: command contains '{blocked}'."

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_directory or None,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS
        )

        output = result.stdout.strip()
        error = result.stderr.strip()

        response = f"Exit code: {result.returncode}\n"
        if output:
            response += f"\nSTDOUT:\n{output}"
        if error:
            response += f"\nSTDERR:\n{error}"

        return response

    except subprocess.TimeoutExpired:
        return f"Command timed out after {TIMEOUT_SECONDS} seconds: {command}"
    except Exception as e:
        return f"Failed to run command: {e}"


TOOLS_IN_MODULE = {
    "run_terminal": (run_terminal_schema, run_terminal),
}
