from agent import Agent

agent = Agent()
print("AI Agent")
while True:

    text = input("You: ")
    if text.lower() == "exit":
        break
    print("\nAI:", agent.handle_message(text), "\n")