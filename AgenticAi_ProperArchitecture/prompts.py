import memory_store
import pdf_index

BASE_PROMPT = """
You are a helpful desktop AI assistant.

Use the available tools whenever needed.

If the user shares a lasting fact, preference, or asks you to remember
something (e.g. "remember that...", "don't forget..."), call the
remember_this tool to save it permanently. Don't just say you'll remember
it in your reply — actually call the tool.

If the user introduces or references a PDF file that may need to be looked
up again later, call index_pdf_knowledge to add it to the searchable
knowledge base. You only need to do this once per PDF.

If no tool is needed, answer normally.
"""

def build_system_prompt(user_text=""):
    """
    Builds the system prompt fresh each time.

    If user_text is given, we retrieve two separate things relevant to
    that message (RAG-style retrieval):
      1. facts about the user, from memory_store
      2. chunks of previously-indexed PDFs, from pdf_index
    Both are searched automatically every turn — the user never has to
    say "check the PDF" once it's been indexed.

    If user_text is empty (e.g. on first startup), we fall back to the
    base prompt with nothing injected — there's no query to search with yet.
    """
    if not user_text:
        return BASE_PROMPT

    prompt = BASE_PROMPT

    relevant_facts = memory_store.get_relevant_memories(user_text)
    if relevant_facts:
        bullet_list = "\n".join(f"- {fact}" for fact in relevant_facts)
        prompt += f"\n\nRelevant things you remember about the user:\n{bullet_list}\n"

    relevant_chunks = pdf_index.search_pdfs(user_text)
    if relevant_chunks:
        chunk_list = "\n\n".join(
            f"[from {c['source']}]\n{c['text']}" for c in relevant_chunks
        )
        prompt += f"\n\nRelevant excerpts from indexed documents:\n{chunk_list}\n"

    return prompt