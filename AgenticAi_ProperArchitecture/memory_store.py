import json
import os
from datetime import datetime
from sentence_transformers import SentenceTransformer
import numpy as np

MEMORY_FILE = "long_term_memory.json"

# Loaded once when this file is first imported. Reused for every
# embed/search call afterward — loading it fresh every time would be slow.
_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def _embed(text):
    """Turn a piece of text into a vector (list of floats)."""
    return _embedding_model.encode(text).tolist()


def _cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


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
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "embedding": _embed(fact.strip())
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


def get_relevant_memories(query, top_k=5, min_similarity=0.3):
    """
    Returns the top_k stored facts whose meaning is closest to `query`.
    Facts saved before embeddings existed (no 'embedding' key) are skipped
    automatically — see the migration step for those.
    """
    memories = _load_raw()
    if not memories:
        return []

    query_vec = _embed(query)

    scored = []
    for m in memories:
        if "embedding" not in m:
            continue  # old fact saved before embeddings were added
        sim = _cosine_similarity(query_vec, m["embedding"])
        if sim >= min_similarity:
            scored.append((sim, m["fact"]))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [fact for _, fact in scored[:top_k]]


def get_memory_block():
    """
    Returns a formatted block of all memories, ready to inject into a
    system prompt. Empty string if there's nothing stored yet.
    """
    facts = get_all_memories()[-30:]  # cap so the prompt doesn't grow forever

    if not facts:
        return ""

    bullet_list = "\n".join(f"- {fact}" for fact in facts)
    return f"\n\nThings you remember about the user from past sessions:\n{bullet_list}\n"