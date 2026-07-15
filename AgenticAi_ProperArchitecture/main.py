import threading
import queue
from customtkinter import *
from agent import Agent
from speaker import speak
import re
# =====================================================
#  AGENT
# =====================================================
agent = Agent()
response_queue = queue.Queue()

# =====================================================
#  MODERN "ASSISTANT" PALETTE (Claude / ChatGPT inspired)
# =====================================================
BG          = "#212121"   # main app background
PANEL       = "#1a1a1a"   # header / input bar
CHAT_BG     = "#212121"   # chat scroll area
BORDER      = "#2f2f2f"   # subtle hairline borders

BUBBLE_AI   = "#2f2f2f"   # neutral grey assistant bubble
BUBBLE_USER = "#ff4000"   # warm terracotta user bubble (Claude accent)

TEXT_PRIMARY   = "#ececec"
TEXT_ON_ACCENT = "#ffffff"
TEXT_MUTED     = "#8e8ea0"

ACCENT      = "#ff4000"   # terracotta accent (buttons, status, avatar)
ACCENT_HOVER = "#751b00"
GREEN_DOT   = "#4fd37b"

FONT_HEAD   = ("Segoe UI Semibold", 18)
FONT_SUB    = ("Segoe UI", 11)
FONT_MSG    = ("Segoe UI", 13)
FONT_TAG    = ("Segoe UI Semibold", 11)
FONT_INPUT  = ("Segoe UI", 13)
FONT_SMALL  = ("Segoe UI", 10)

set_appearance_mode("dark")

# =====================================================
#  APP SHELL
# =====================================================
app = CTk()
app.geometry("880x680")
app.minsize(700, 520)
app.title("AI Assistant")
app.configure(fg_color=BG)

# ---- Header -----------------------------------------
header = CTkFrame(app, fg_color=PANEL, height=64, corner_radius=0)
header.pack(fill="x")
header.pack_propagate(False)

title_wrap = CTkFrame(header, fg_color="transparent")
title_wrap.pack(side="left", padx=20)

avatar = CTkLabel(
    title_wrap, text="AI", width=36, height=36, corner_radius=18,
    fg_color=ACCENT, text_color=TEXT_ON_ACCENT, font=("Segoe UI Semibold", 13)
)
avatar.grid(row=0, column=0, rowspan=2, padx=(0, 10))

CTkLabel(title_wrap, text="Iris", font=FONT_HEAD,
         text_color=TEXT_PRIMARY).grid(row=0, column=1, sticky="w")

status_wrap = CTkFrame(title_wrap, fg_color="transparent")
status_wrap.grid(row=1, column=1, sticky="w")
CTkLabel(status_wrap, text="●", font=("Segoe UI", 9), text_color=GREEN_DOT).pack(side="left")
status_label = CTkLabel(status_wrap, text=" Online", font=FONT_SUB, text_color=TEXT_MUTED)
status_label.pack(side="left")

# ---- Chat scroll area --------------------------------
chat_frame = CTkScrollableFrame(
    app,
    fg_color=CHAT_BG,
    scrollbar_button_color=BORDER,
    scrollbar_button_hover_color=ACCENT,
)
chat_frame.pack(fill="both", expand=True, padx=0, pady=0)
chat_frame.grid_columnconfigure(0, weight=1)

# ---- Input bar ----------------------------------------
input_frame = CTkFrame(app, fg_color=PANEL, corner_radius=0, height=84)
input_frame.pack(fill="x")
input_frame.pack_propagate(False)

input_inner = CTkFrame(input_frame, fg_color=BUBBLE_AI, corner_radius=22, border_color=BORDER, border_width=1)
input_inner.pack(fill="x", padx=20, pady=18)

message_entry = CTkEntry(
    input_inner,
    placeholder_text="Talk to Iris...",
    placeholder_text_color=TEXT_MUTED,
    height=44,
    fg_color="transparent",
    border_width=0,
    text_color=TEXT_PRIMARY,
    font=FONT_INPUT,
)
message_entry.pack(side="left", fill="x", expand=True, padx=(16, 6))

send_button = CTkButton(
    input_inner,
    text="Send",
    width=80,
    height=34,
    corner_radius=17,
    fg_color=ACCENT,
    hover_color=ACCENT_HOVER,
    text_color=TEXT_ON_ACCENT,
    font=("Segoe UI Semibold", 13),
)
send_button.pack(side="right", padx=(0, 8), pady=5)

# =====================================================
#  CHAT BUBBLE HELPERS
# =====================================================
row_index = 0
thinking_row = None


def _scroll_to_bottom():
    app.update_idletasks()
    chat_frame._parent_canvas.yview_moveto(1.0)


def copy_to_clipboard(text, button):
    app.clipboard_clear()
    app.clipboard_append(text)
    app.update()

    original = button.cget("text")
    button.configure(text="Copied!", text_color=GREEN_DOT)
    app.after(1500, lambda: button.configure(text=original, text_color=TEXT_MUTED))


def add_bubble(message, is_user):
    """Creates one chat-bubble row. Returns (row_frame, message_label)."""
    global row_index

    row = CTkFrame(chat_frame, fg_color="transparent")
    row.grid(row=row_index, column=0, sticky="ew", pady=8, padx=24)
    row.grid_columnconfigure(0, weight=1)
    row_index += 1

    bubble_bg = BUBBLE_USER if is_user else BUBBLE_AI
    text_color = TEXT_ON_ACCENT if is_user else TEXT_PRIMARY
    anchor_side = "e" if is_user else "w"
    tag_text = "You" if is_user else "Iris"

    bubble_wrap = CTkFrame(row, fg_color="transparent")
    bubble_wrap.grid(row=0, column=0, sticky=anchor_side)

    CTkLabel(bubble_wrap, text=tag_text, font=FONT_TAG,
             text_color=TEXT_MUTED).pack(anchor=anchor_side, padx=6, pady=(0, 3))

    bubble = CTkFrame(
        bubble_wrap,
        fg_color=bubble_bg,
        corner_radius=16,
    )
    bubble.pack(anchor=anchor_side)

    msg_label = CTkLabel(
        bubble,
        text=message,
        font=FONT_MSG,
        text_color=text_color,
        wraplength=520,
        justify="left",
        anchor="w",
    )
    msg_label.pack(padx=16, pady=(12, 6 if not is_user else 12))

    # Copy button only on assistant messages
    if not is_user:
        copy_btn = CTkButton(
            bubble,
            text="⧉ Copy",
            width=60,
            height=22,
            corner_radius=6,
            fg_color="transparent",
            hover_color=BORDER,
            text_color=TEXT_MUTED,
            font=FONT_SMALL,
        )
        copy_btn.configure(command=lambda: copy_to_clipboard(message, copy_btn))
        copy_btn.pack(anchor="w", padx=10, pady=(0, 8))

    _scroll_to_bottom()
    return row, msg_label


def add_message(sender, message):
    add_bubble(message, is_user=(sender.lower() == "you"))


def add_thinking():
    global thinking_row
    thinking_row, label = add_bubble("Thinking", is_user=False)
    _animate_thinking(label, 0)


def _animate_thinking(label, step):
    if thinking_row is None or not thinking_row.winfo_exists():
        return
    dots = "." * (step % 4)
    try:
        label.configure(text=f"Thinking{dots}")
    except Exception:
        return
    app.after(400, lambda: _animate_thinking(label, step + 1))


def replace_thinking(response):
    global thinking_row
    if thinking_row is not None and thinking_row.winfo_exists():
        thinking_row.destroy()
        thinking_row = None
    add_bubble(response, is_user=False)


# =====================================================
#  WORKER THREAD
# =====================================================
def generate_response(text):
    try:
        response = agent.handle_message(text)
    except Exception as e:
        response = f"Error: {e}"
    response_queue.put(response)

def clean_text(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`", "", text)
    text = re.sub(r"#+", "", text)
    return text.strip()

def check_queue():
    try:
        response = response_queue.get_nowait()
        replace_thinking(response)
        # Speak the AI response
        speak(clean_text(response))

        send_button.configure(state="normal")
        message_entry.configure(state="normal")
        status_label.configure(text=" Online")
        message_entry.focus()
    except queue.Empty:
        pass

    app.after(100, check_queue)


def send_message(event=None):
    text = message_entry.get().strip()
    if not text:
        return

    add_message("You", text)
    message_entry.delete(0, END)

    status_label.configure(text=" Thinking...")
    add_thinking()

    send_button.configure(state="disabled")
    message_entry.configure(state="disabled")

    threading.Thread(target=generate_response, args=(text,), daemon=True).start()


send_button.configure(command=send_message)
message_entry.bind("<Return>", send_message)

# =====================================================
#  WELCOME
# =====================================================
add_message("Iris", "Hello! How can I help you today?")

check_queue()
app.mainloop()