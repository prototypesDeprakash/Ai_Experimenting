from dotenv import load_dotenv;
import os
from openai import OpenAI
from agents import Agent
load_dotenv() 



key=os.getenv("API")






client = OpenAI(
    api_key=key,
    base_url="https://openrouter.ai/api/v1",
)

# Conversation history
messages = [
    {
        "role": "system",
        "content": "You are a helpful AI assistant."
    }
]

print("AI Chatbot")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        print("Goodbye!")
        break

    # Add user's message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
        )

        assistant_reply = response.choices[0].message.content

        print(f"\nAI: {assistant_reply}\n")

        # Save assistant response for future context
        messages = [
    {
        "role": "system",
        "content": """
You are a world-class Senior Software Engineer,
 Computer Science mentor, and Technical Architect with 
 over 20 years of experience building production-scale software.
Your goal is to produce engineers who understand the "why",
 not developers who copy and paste code.
"""
    }
        ]

    except Exception as e:
        print("Error:", e)