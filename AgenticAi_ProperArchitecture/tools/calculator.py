import subprocess

schema = {
    "type": "function",
    "function": {
        "name": "open_calculator",
        "description": "Open the Windows Calculator.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

def execute():
    subprocess.Popen("calc.exe")
    return "Calculator opened successfully."