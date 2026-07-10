import memory_store

# =================================================
# remember_this
# =================================================

remember_this_schema = {
    "type": "function",
    "function": {
        "name": "remember_this",
        "description": (
            "Save a fact permanently to long-term memory, so it's available in ALL future "
            "sessions, not just this conversation. Use this whenever the user says things like "
            "'remember that...', 'don't forget...', or shares a lasting preference/fact about "
            "themselves (name, likes, ongoing projects, etc.)."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "fact": {
                    "type": "string",
                    "description": "The fact to remember, written as a short standalone statement (e.g. 'User's dog is named Max')."
                }
            },
            "required": ["fact"]
        }
    }
}

def remember_this(fact):
    return memory_store.add_memory(fact)


# =================================================
# forget_this
# =================================================

forget_this_schema = {
    "type": "function",
    "function": {
        "name": "forget_this",
        "description": "Remove a previously saved fact from long-term memory. Use when the user asks to forget or correct something.",
        "parameters": {
            "type": "object",
            "properties": {
                "fact_substring": {
                    "type": "string",
                    "description": "Text to match against stored facts (partial match is fine, e.g. 'dog' matches 'User's dog is named Max')."
                }
            },
            "required": ["fact_substring"]
        }
    }
}

def forget_this(fact_substring):
    return memory_store.forget_memory(fact_substring)


TOOLS_IN_MODULE = {
    "remember_this": (remember_this_schema, remember_this),
    "forget_this": (forget_this_schema, forget_this),
}