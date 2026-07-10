import json

from memory import messages, refresh_system_prompt
from llm import chat, extract_facts
from tool_registry import TOOLS, SCHEMAS
import memory_store


class Agent:

    def handle_message(self, text):

        messages.append({
            "role": "user",
            "content": text
        })

        response = chat(messages, SCHEMAS)
        message = response.choices[0].message

        # -------------------------
        # TOOL CALL(S)
        # -------------------------

        if message.tool_calls:

            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name

                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    result = f"Error: model produced invalid arguments for {tool_name}"
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })
                    continue

                print("\nTool Selected :", tool_name)
                print("Arguments     :", arguments)

                if tool_name not in TOOLS:
                    result = f"Unknown tool: {tool_name}"
                else:
                    try:
                        result = TOOLS[tool_name](**arguments)
                    except Exception as e:
                        result = f"Tool {tool_name} failed: {e}"

                print("Tool Result   :", result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            refresh_system_prompt()

            second_response = chat(messages, SCHEMAS)
            final_answer = second_response.choices[0].message.content

            messages.append({
                "role": "assistant",
                "content": final_answer
            })

            self._run_memory_extraction(text, final_answer)
            return final_answer

        # -------------------------
        # NORMAL RESPONSE
        # -------------------------

        answer = message.content

        messages.append({
            "role": "assistant",
            "content": answer
        })

        self._run_memory_extraction(text, answer)
        return answer

    def _run_memory_extraction(self, user_text, assistant_text):
        """
        Background safety net: even if the model didn't call remember_this
        inline, this catches lasting facts and saves them anyway.
        """
        facts = extract_facts(user_text, assistant_text)

        if facts:
            for fact in facts:
                result = memory_store.add_memory(fact)
                print("Auto-remembered:", result)
            refresh_system_prompt()