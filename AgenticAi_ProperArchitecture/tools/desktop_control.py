import psutil

# NOTE: requires `pip install psutil`


# =================================================
# close_software
# =================================================

close_software_schema = {
    "type": "function",
    "function": {
        "name": "close_software",
        "description": "Close a running application by name (e.g. 'chrome', 'notepad', 'spotify').",
        "parameters": {
            "type": "object",
            "properties": {
                "application_name": {
                    "type": "string",
                    "description": "Name of the application/process to close (partial match, case-insensitive)."
                }
            },
            "required": ["application_name"]
        }
    }
}

def close_software(application_name):
    application_name = application_name.lower().strip()
    closed = []

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = (proc.info["name"] or "").lower()
            if application_name in name:
                proc.terminate()
                closed.append(f"{proc.info['name']} (pid {proc.info['pid']})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not closed:
        return f"No running process matching '{application_name}' was found."

    return "Closed: " + ", ".join(closed)


# =================================================
# list_running_software
# =================================================

list_running_software_schema = {
    "type": "function",
    "function": {
        "name": "list_running_software",
        "description": "List currently running applications/processes on the computer.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

def list_running_software():
    names = set()

    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info["name"]
            if name:
                names.add(name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if not names:
        return "No running processes detected."

    return "\n".join(sorted(names))


TOOLS_IN_MODULE = {
    "close_software": (close_software_schema, close_software),
    "list_running_software": (list_running_software_schema, list_running_software),
}
