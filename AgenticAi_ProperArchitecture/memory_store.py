import json
import os
from datetime import datetime

MEMORY_FILE = "long_term_memory.json"


def _load_raw():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_raw(memories):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, indent=2)


def add_memory(fact):
    """Append a new fact to long-term memory. Avoids exact duplicates."""
    memories = _load_raw()

    for m in memories:
        if m["fact"].strip().lower() == fact.strip().lower():
            return "Already remembered that."

    memories.append({
        "fact": fact.strip(),
        "saved_at": datetime.now().isoformat(timespec="seconds")
    })
    _save_raw(memories)
    return f"Remembered: {fact}"


def forget_memory(fact_substring):
    """Remove any memory whose text contains fact_substring (case-insensitive)."""
    memories = _load_raw()
    fact_substring = fact_substring.strip().lower()

    remaining = [m for m in memories if fact_substring not in m["fact"].lower()]
    removed_count = len(memories) - len(remaining)

    if removed_count == 0:
        return f"No memory found matching '{fact_substring}'."

    _save_raw(remaining)
    return f"Forgot {removed_count} memory/memories matching '{fact_substring}'."


def get_all_memories():
    """Return every stored fact as a list of strings."""
    return [m["fact"] for m in _load_raw()]


def get_memory_block():
    """
    Returns a formatted block of all memories, ready to inject into a
    system prompt. Empty string if there's nothing stored yet.
    """
    facts = get_all_memories()

    if not facts:
        return ""

    bullet_list = "\n".join(f"- {fact}" for fact in facts)
    return f"\n\nThings you remember about the user from past sessions:\n{bullet_list}\n"