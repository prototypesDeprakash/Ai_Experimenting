from memory import messages
from llm import chat
from tool_registry import TOOLS, SCHEMAS


class Agent:

    def handle_message(self, text):

        messages.append({
            "role": "user",
            "content": text
        })

        response = chat(messages, SCHEMAS)

        message = response.choices[0].message

        # Tool Call?
        if message.tool_calls:

            tool_call = message.tool_calls[0]

            tool_name = tool_call.function.name

            result = TOOLS[tool_name]()

            print(result)

            messages.append(message)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

            second = chat(messages, SCHEMAS)

            answer = second.choices[0].message.content

            messages.append({
                "role": "assistant",
                "content": answer
            })

            return answer

        answer = message.content

        messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer