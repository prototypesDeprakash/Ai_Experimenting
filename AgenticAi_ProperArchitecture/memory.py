from prompts import build_system_prompt

messages = [
    {
        "role": "system",
        "content": build_system_prompt()
    }
]


def refresh_system_prompt(user_text=""):
    """
    Call this right before asking the model to respond, so the system
    prompt (messages[0]) contains memories relevant to what the user just
    said. Also called after remember_this/forget_this run, using the same
    user_text so the refreshed list still reflects the current query.
    """
    messages[0]["content"] = build_system_prompt(user_text)