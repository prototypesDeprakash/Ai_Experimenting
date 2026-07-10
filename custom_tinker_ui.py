import tkinter as tk
from tkinter import scrolledtext, messagebox

# Create the main window
root = tk.Tk()
root.title("Custom Tinker UI for Chatbot")
root.geometry("600x400")

# Chat history display
chat_history = scrolledtext.ScrolledText(root, wrap="word", state="disabled")
chat_history.pack(padx=10, pady=10, fill="both", expand=True)

# Input area
input_area = tk.Text(root, height=3, font=("Arial", 12))
input_area.pack(padx=10, pady=10, fill="x")

# Send button
send_button = tk.Button(root, text="Send", command=lambda: send_message())
send_button.pack(pady=10)

# Function to send message
def send_message():
    user_input = input_area.get("1.0", "end-1c")
    if user_input.strip() == "":
        return

    # Display user message
    chat_history.configure(state="normal")
    chat_history.insert(tk.END, "You: " + user_input + "\n")
    chat_history.configure(state="disabled")
    chat_history.see(tk.END)

    # Simulate bot response (you can replace this with actual logic)
    bot_response = "Bot: I received your message: " + user_input
    chat_history.configure(state="normal")
    chat_history.insert(tk.END, bot_response + "\n")
    chat_history.configure(state="disabled")
    chat_history.see(tk.END)

    # Clear input area
    input_area.delete("1.0", tk.END)

# Run the application
root.mainloop()