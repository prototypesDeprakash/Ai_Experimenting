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

def build_system_prompt(user_text=""):
    """
    Builds the system prompt fresh each time.

    If user_text is given, we only inject memories that are relevant to
    that message (RAG-style retrieval) instead of dumping every stored
    fact. If user_text is empty (e.g. on first startup, before the user
    has said anything), we fall back to no memories at all — there's no
    query to search with yet.
    """
    if not user_text:
        return BASE_PROMPT

    relevant_facts = memory_store.get_relevant_memories(user_text)

    if not relevant_facts:
        return BASE_PROMPT

    bullet_list = "\n".join(f"- {fact}" for fact in relevant_facts)
    memory_block = f"\n\nRelevant things you remember about the user:\n{bullet_list}\n"

    return BASE_PROMPT + memory_block