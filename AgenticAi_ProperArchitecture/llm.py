# from config import client

# def chat(messages, schemas):

#     response = client.chat.completions.create(
#         model="openrouter/free",
#         messages=messages,
#         tools=schemas
#     )

#     return response

from config import client

def chat(messages, schemas):

    response = client.chat.completions.create(
        model="qwen-3-8b-instruct",
        messages=messages,
        tools=schemas
    )

    return response