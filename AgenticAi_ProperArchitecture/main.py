# from agent import Agent

# agent = Agent()
# print("AI Agent")
# while True:

#     text = input("You: ")
#     if text.lower() == "exit":
#         break
#     print("\nAI:", agent.handle_message(text), "\n")

import threading
import queue
from customtkinter import *
from agent import Agent

# -----------------------------
# Create Agent
# -----------------------------
agent = Agent()

# Thread-safe queue
response_queue = queue.Queue()

# -----------------------------
# App
# -----------------------------
app = CTk()
app.geometry("900x650")
app.title("AI Agent")
app.resizable(False, False)
set_appearance_mode("System")

# -----------------------------
# Theme
# -----------------------------
BG = "#121212"
FRAME = "#1B1B1B"
HEADER = "#181818"

ACCENT = "#E53935"
TEXT = "#F5F5F5"

BUTTON = "#E53935"
BUTTON_HOVER = "#C62828"

GREY = "#222222"

app.configure(fg_color=BG)

# -----------------------------
# Layout
# -----------------------------

header = CTkFrame(app, fg_color=HEADER,
                  border_color=ACCENT,
                  border_width=1)
header.pack(fill="x", padx=20, pady=10)

chat_frame = CTkFrame(app,
                      fg_color=FRAME,
                      border_color=ACCENT,
                      border_width=1)

chat_frame.pack(fill="both", expand=True, padx=20)

input_frame = CTkFrame(app,
                       fg_color=FRAME,
                       border_color=ACCENT,
                       border_width=1)

input_frame.pack(fill="x", padx=20, pady=10)

# -----------------------------
# Title
# -----------------------------

CTkLabel(
    header,
    text="AI Agent",
    font=("Consolas", 22, "bold"),
    text_color=ACCENT
).pack(pady=10)

# -----------------------------
# Chat Box
# -----------------------------

chat_box = CTkTextbox(
    chat_frame,
    fg_color=GREY,
    border_color=ACCENT,
    border_width=1,
    text_color="#1aff00",
    font=("Consolas", 14),
    wrap="word"
)

chat_box.pack(fill="both", expand=True, padx=15, pady=15)
chat_box.configure(state="disabled")

# -----------------------------
# Input
# -----------------------------

message_entry = CTkEntry(
    input_frame,
    placeholder_text="Type your message...",
    height=45,
    fg_color=FRAME,
    border_color=ACCENT,
    border_width=1,
    text_color=TEXT,
    font=("Consolas", 14)
)

message_entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(10, 10),
    pady=10
)

# -----------------------------
# Send Button
# -----------------------------

send_button = CTkButton(
    input_frame,
    text="SEND",
    width=120,
    height=45,
    fg_color=BUTTON,
    hover_color=BUTTON_HOVER,
    text_color="white",
    font=("Consolas", 15, "bold")
)

send_button.pack(side="right", padx=(0, 10), pady=10)


# -----------------------------
# Chat Helpers
# -----------------------------

thinking_line = None


def add_message(sender, message):

    chat_box.configure(state="normal")
    chat_box.insert("end", f"{sender}: {message}\n\n")
    chat_box.configure(state="disabled")
    chat_box.see("end")


def add_thinking():

    global thinking_line

    chat_box.configure(state="normal")

    thinking_line = chat_box.index("end-1c")

    chat_box.insert("end", "AI: Thinking...\n\n")

    chat_box.configure(state="disabled")
    chat_box.see("end")


def replace_thinking(response):

    global thinking_line

    chat_box.configure(state="normal")

    start = thinking_line
    end = chat_box.index(f"{thinking_line} +2 lines")

    chat_box.delete(start, end)

    chat_box.insert(start, f"AI: {response}\n\n")

    chat_box.configure(state="disabled")
    chat_box.see("end")


# -----------------------------
# Worker Thread
# -----------------------------

def generate_response(text):

    try:
        response = agent.handle_message(text)
    except Exception as e:
        response = str(e)

    response_queue.put(response)


# -----------------------------
# Poll Queue
# -----------------------------

def check_queue():

    try:
        response = response_queue.get_nowait()
        replace_thinking(response)
        send_button.configure(state="normal")
        message_entry.configure(state="normal")
        message_entry.focus()

    except queue.Empty:
        pass

    app.after(100, check_queue)


# -----------------------------
# Send Message
# -----------------------------

def send_message(event=None):

    text = message_entry.get().strip()

    if not text:
        return

    add_message("You", text)

    message_entry.delete(0, END)

    add_thinking()

    send_button.configure(state="disabled")
    message_entry.configure(state="disabled")

    threading.Thread(
        target=generate_response,
        args=(text,),
        daemon=True
    ).start()


send_button.configure(command=send_message)

message_entry.bind("<Return>", send_message)

# -----------------------------
# Welcome
# -----------------------------

add_message("AI", "Hello! How can I help you?")

check_queue()

app.mainloop()