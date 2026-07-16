import json

from memory import messages, refresh_system_prompt
from llm import chat, extract_facts
from tool_registry import TOOLS, SCHEMAS
import memory_store
import threading

MAX_TOOL_ITERATIONS = 8  # safety cap so a confused model can't loop forever


class Agent:

    def handle_message(self, text):

        messages.append({
            "role": "user",
            "content": text
        })

        # RAG step: refresh the system prompt now, using this message as
        # the search query, so only relevant memories are in context for
        # this turn (instead of a static dump of the last 30 facts).
        refresh_system_prompt(text)

        final_answer = None

        for _ in range(MAX_TOOL_ITERATIONS):

            response = chat(messages, SCHEMAS)
            message = response.choices[0].message

            # -------------------------
            # TOOL CALL(S) — execute, then loop back and ask again
            # -------------------------
            if message.tool_calls:

                messages.append(message.model_dump(exclude_unset=True))

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

                refresh_system_prompt(text)
                continue  # ask the model again — it may call more tools or finally answer

            # -------------------------
            # FINAL TEXT ANSWER — loop ends here
            # -------------------------
            final_answer = message.content
            messages.append({
                "role": "assistant",
                "content": final_answer
            })
            break

        if final_answer is None:
            final_answer = "(Stopped after several tool calls without a final answer — check the console log above.)"
            messages.append({"role": "assistant", "content": final_answer})

        threading.Thread(
            target=self._run_memory_extraction,
            args=(text, final_answer),
            daemon=True
        ).start()
        return final_answer

    def _run_memory_extraction(self, user_text, assistant_text):
        facts = extract_facts(user_text, assistant_text)

        if facts:
            for fact in facts:
                result = memory_store.add_memory(fact)
                print("Auto-remembered:", result)
            refresh_system_prompt(user_text)