from config import client

def chat(messages, schemas):

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=messages,
        tools=schemas
    )

    return response