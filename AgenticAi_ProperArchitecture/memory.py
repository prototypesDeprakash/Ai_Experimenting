from prompts import build_system_prompt

messages = [
    {
        "role": "system",
        "content": build_system_prompt()
    }
]


def refresh_system_prompt():
    """
    Call this after remember_this/forget_this run, so the system prompt
    (messages[0]) reflects the latest long-term memory immediately,
    instead of only on the next restart.
    """
    messages[0]["content"] = build_system_prompt()