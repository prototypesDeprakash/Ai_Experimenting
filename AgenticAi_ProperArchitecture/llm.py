import json
from config import client

MODEL = "qwen-3-8b-instruct"


def chat(messages, schemas):

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=schemas
    )

    return response


EXTRACTION_PROMPT = """
Look at this exchange between a user and an assistant. Extract any lasting
facts about the user worth remembering permanently (name, preferences,
ongoing projects, relationships, etc). Ignore small talk, jokes, or anything
temporary/situational.

Respond ONLY with a JSON array of short standalone fact strings. No markdown,
no explanation. If there's nothing worth remembering, respond with [].

Example output: ["User's name is Prakash", "User prefers dark mode"]
"""


def extract_facts(user_text, assistant_text):
    """
    Separate, dedicated call whose only job is spotting memorable facts.
    Decoupled from the main chat's tool-calling decision, since smaller
    local models are inconsistent about calling remember_this inline.
    """
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {"role": "user", "content": f"User: {user_text}\nAssistant: {assistant_text}"}
            ]
        )

        raw = response.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        facts = json.loads(raw)
        return facts if isinstance(facts, list) else []

    except Exception:
        # Extraction is a nice-to-have — never let it break the main chat flow
        return []