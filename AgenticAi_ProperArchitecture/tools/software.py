import subprocess

# -------------------------------------------------
# Supported Applications
# -------------------------------------------------

SOFTWARES = {
    # Calculator
    "calculator": "calc.exe",
    "calc": "calc.exe",

    # Notepad
    "notepad": "notepad.exe",

    # Paint
    "paint": "mspaint.exe",

    # File Explorer
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",

    # Command Prompt
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",

    # Browser
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",

    # Microsoft Edge
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",

    # Blender
    "blender": r"D:\Blender\blender-launcher.exe"
}

# Automatically generate the supported application list
supported_apps = ", ".join(sorted(SOFTWARES.keys()))

# -------------------------------------------------
# Tool Schema
# -------------------------------------------------

schema = {
    "type": "function",
    "function": {
        "name": "open_software",
        "description": f"""
Open one of the supported software applications installed on the computer.

Supported applications:
{supported_apps}

Always choose the closest matching supported application name.
For example:
- "File Explorer" -> "explorer"
- "Google Chrome" -> "chrome"
- "Calculator" -> "calculator"
- "Command Prompt" -> "cmd"
""",
        "parameters": {
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "The software application to open."
                }
            },
            "required": ["application_name"]
        }
    }
}

# -------------------------------------------------
# Tool Execution
# -------------------------------------------------

def execute(application_name):

    application_name = application_name.lower().strip()

    app = SOFTWARES.get(application_name)

    if app is None:
        return (
            f"{application_name} is not supported.\n"
            f"Supported applications are:\n{supported_apps}"
        )

    try:
        subprocess.Popen(app)
        return f"{application_name} opened successfully."

    except Exception as e:
        return f"Failed to open {application_name}: {e}"