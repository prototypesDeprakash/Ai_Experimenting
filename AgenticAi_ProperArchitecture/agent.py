import json

from memory import messages
from llm import chat
from tool_registry import TOOLS, SCHEMAS


class Agent:

    def handle_message(self, text):

        # Add user message
        messages.append({
            "role": "user",
            "content": text
        })

        # Ask the LLM
        response = chat(messages, SCHEMAS)

        message = response.choices[0].message

        # -------------------------
        # TOOL CALL
        # -------------------------

        if message.tool_calls:

            tool_call = message.tool_calls[0]

            tool_name = tool_call.function.name

            # Convert JSON string to Python dictionary
            arguments = json.loads(tool_call.function.arguments)

            print("\nTool Selected :", tool_name)
            print("Arguments     :", arguments)

            # Execute tool dynamically
            result = TOOLS[tool_name](**arguments)

            print("Tool Result   :", result)

            # Save assistant tool call
            messages.append(message)

            # Save tool response
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

            # Ask LLM again with tool result
            second_response = chat(messages, SCHEMAS)

            final_answer = second_response.choices[0].message.content

            messages.append({
                "role": "assistant",
                "content": final_answer
            })

            return final_answer

        # -------------------------
        # NORMAL RESPONSE
        # -------------------------

        answer = message.content

        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer