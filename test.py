from dotenv import load_dotenv
from openai import OpenAI
import subprocess
import os

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv()

client = OpenAI(
    api_key=os.getenv("API"),
    base_url="https://openrouter.ai/api/v1"
)

# ----------------------------
# TOOLS
# ----------------------------

def print_hello():
    print("\n>>> Hello World <<<")
    return "Hello World tool executed."

def open_calculator():
    subprocess.Popen("calc.exe")
    return "Calculator opened successfully."

# Tool Dictionary
tools = {
    "hello_world": print_hello,
    "open_calculator": open_calculator
}

# ----------------------------
# SYSTEM PROMPT
# ----------------------------

messages = [
    {
        "role": "system",
        "content": """
You are an AI Agent.

You have access to the following tools.

-------------------------------------------------

Tool Name: hello_world

Description:
Prints Hello World.

If the user wants to:
- call hello world
- run hello world
- execute hello world

Return EXACTLY

TOOL: hello_world

-------------------------------------------------

Tool Name: open_calculator

Description:
Opens the Windows Calculator.

If the user wants to:
- open calculator
- launch calculator
- start calculator
- open calc

Return EXACTLY

TOOL: open_calculator

-------------------------------------------------

For ALL OTHER requests answer normally.

NEVER explain a tool call.

If a tool is needed, your ENTIRE response must contain ONLY:

TOOL: tool_name
"""
    }
]

print("========== AI AGENT ==========")
print("Type 'exit' to quit.\n")

# ----------------------------
# MAIN LOOP
# ----------------------------

while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    try:

        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages
        )

        assistant_reply = response.choices[0].message.content.strip()

        print("\nRAW MODEL OUTPUT:")
        print(assistant_reply)

        # ----------------------------
        # TOOL DETECTION
        # ----------------------------

        if "TOOL:" in assistant_reply:

            tool_name = assistant_reply.split("TOOL:")[1].strip()

            if tool_name in tools:

                print(f"\nExecuting Tool: {tool_name}\n")

                result = tools[tool_name]()

                print(result)

                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_reply
                    }
                )

                messages.append(
                    {
                        "role": "tool",
                        "content": result
                    }
                )

                continue

            else:
                print("Unknown Tool:", tool_name)
                continue

        # ----------------------------
        # NORMAL RESPONSE
        # ----------------------------

        print("\nAI:", assistant_reply, "\n")

        messages.append(
            {
                "role": "assistant",
                "content": assistant_reply
            }
        )

    except Exception as e:
        print("ERROR:", e)