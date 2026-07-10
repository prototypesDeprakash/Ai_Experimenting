import memory_store

BASE_PROMPT = """
You are a helpful desktop AI assistant.

Use the available tools whenever needed.

If the user shares a lasting fact, preference, or asks you to remember
something (e.g. "remember that...", "don't forget..."), call the
remember_this tool to save it permanently. Don't just say you'll remember
it in your reply — actually call the tool.

If no tool is needed, answer normally.
"""

def build_system_prompt():
    """
    Builds the system prompt fresh each time — includes whatever is
    currently in long-term memory, so it reflects deletions/additions
    made mid-session too.
    """
    return BASE_PROMPT + memory_store.get_memory_block()