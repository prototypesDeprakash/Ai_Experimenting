# Iris — Local Desktop AI Assistant

A privacy-first, fully local desktop AI assistant that runs entirely on your own machine. Iris combines a local LLM (served via [LM Studio](https://lmstudio.ai/)), a tool-calling agent loop, a persistent two-tier memory system, PDF knowledge retrieval, and a dark-themed desktop chat UI with text-to-speech — all without sending your data to a third-party API.

> Built as a personal learning project to explore agentic architectures, RAG-based memory, and local-first AI tooling.

---

##  Features

- **Fully local inference** — talks to any OpenAI-compatible local model server (default: `qwen-3-8b-instruct` via LM Studio). No cloud API required.
- **Tool-calling agent loop** — the model can autonomously call tools, inspect results, and chain multiple calls before responding, with a safety cap on iterations.
- **Persistent long-term memory** — facts about you are embedded (`sentence-transformers` / `all-MiniLM-L6-v2`) and stored locally, then retrieved by semantic similarity so only relevant memories are injected into the prompt each turn.
- **Automatic memory extraction** — a background pass reviews every exchange and saves lasting facts, even if the model forgets to call the memory tool inline.
- **PDF knowledge base** — index any PDF once; its content is automatically chunked, embedded, and semantically searched on future turns without needing to reference the file again.
- **Desktop control tools** — open/close applications, list running processes, run shell commands (with a blocklist for destructive operations), and manage files/folders.
- **Text-to-speech** — spoken responses via `pyttsx3`, running on a dedicated worker thread.
- **Custom chat UI** — a `customtkinter`-based desktop interface with a dark theme, chat bubbles, and copy-to-clipboard support.
- **Modular tool registry** — new tools are added by dropping a module with a `schema` + function (or a `TOOLS_IN_MODULE` dict) into the `tools/` package; no manual wiring required.

---

##  Architecture

```
┌─────────────┐     ┌───────────────┐     ┌────────────────────┐
│   main.py   │────▶│   agent.py    │────▶│  llm.py (LM Studio) │
│  (chat UI)  │     │ (tool loop)   │     └────────────────────┘
└─────────────┘     └───────┬───────┘
       │                    │
       ▼                    ▼
  speaker.py          tool_registry.py
  (TTS worker)               │
                    ┌────────┴─────────┐
                    ▼                  ▼
             tools/*.py          memory.py
        (filesystem, terminal,   (system prompt +
      desktop control, memory)    RAG injection)
                                        │
                              ┌─────────┴─────────┐
                              ▼                    ▼
                       memory_store.py       pdf_index.py
                     (facts, embeddings)   (PDF chunks, embeddings)
```

**Turn flow:**
1. User message is added to the conversation and the system prompt is refreshed with semantically relevant memories and PDF excerpts (RAG).
2. The model is queried with the full tool schema. If it calls tools, they execute and results are appended; the loop repeats (up to a safety cap).
3. Once the model returns a final text answer, it's shown in the UI and spoken aloud.
4. In the background, a separate extraction call scans the exchange for durable facts and saves them to long-term memory.

---

##  Available Tools

| Tool | Description |
|---|---|
| `remember_this` / `forget_this` | Save or remove a fact in long-term memory |
| `index_pdf_knowledge` | Chunk, embed, and index a PDF for future semantic search |
| `read_pdf` | One-off text extraction from a PDF |
| `read_file` / `write_file` | Read or write plain-text files |
| `search_files` / `list_directory` | Locate and browse files/folders |
| `create_folder` / `move_file` / `rename_file` | File and folder management |
| `open_software` / `close_software` | Launch or terminate applications |
| `list_running_software` | List active processes |
| `run_terminal` | Execute shell commands (with a blocklist for destructive commands) |

>  `delete_file` is intentionally stubbed to refuse deletion — irreversible actions are disabled by default at the tool level.

---

##  Getting Started

### Prerequisites
- Python 3.10+
- [LM Studio](https://lmstudio.ai/) (or any OpenAI-compatible local inference server) running a chat + tool-calling capable model
- Windows (some tools like `open_software`/`close_software` and TTS voice selection are Windows-oriented; adapt paths for other OSes)

### Installation

```bash
git clone https://github.com/prototypesDeprakash/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

<details>
<summary>Core dependencies</summary>

```
openai
python-dotenv
customtkinter
pyttsx3
psutil
pypdf
sentence-transformers
numpy
```

</details>

### Configuration

1. Start LM Studio (or your preferred OpenAI-compatible server) and load a tool-calling capable model.
2. Update `config.py` with your local server's base URL and the model name in `llm.py` (`MODEL = "your-model-name"`).
3. Run the app:

```bash
python main.py
```

---

##  Project Structure

```
.
├── main.py              # Desktop chat UI (customtkinter)
├── agent.py             # Core agent loop: tool calls, memory extraction
├── llm.py               # LLM chat + fact-extraction calls
├── config.py             # OpenAI-compatible client configuration
├── memory.py             # System prompt assembly / refresh
├── memory_store.py       # Long-term fact storage + embeddings
├── memory_tool.py        # remember_this / forget_this tool
├── prompts.py             # Base system prompt + RAG injection
├── pdf_index.py           # PDF chunking, embedding, and search
├── tool_registry.py       # Aggregates all tool schemas/functions
├── speaker.py             # Text-to-speech worker thread
└── tools/
    ├── filesystem.py      # File/folder + PDF tools
    ├── terminal.py         # Shell command execution
    ├── desktop_control.py  # Process management
    └── software.py         # Application launcher
```

---

##  Known Limitations / Security Notes

This is a personal/learning project, not a hardened production tool:

- Filesystem tools operate on absolute paths without sandboxing — the model can read/write anywhere the OS user has access to.
- `run_terminal` uses a substring blocklist, which is a basic safeguard, not a complete defense against destructive commands.
- Tool output (e.g. file contents, PDF text) is not sanitized before being fed back into the model, so treat it as untrusted input.
- No confirmation gate exists yet for irreversible actions beyond the disabled `delete_file`.

Contributions to harden these areas are welcome.

---

##  Roadmap

- [ ] Sandboxed filesystem access
- [ ] Confirmation prompts for sensitive tool calls
- [ ] Cross-platform support for desktop control tools
- [ ] Unity avatar frontend integration (head-tracking, lip sync)

---

##  License

This project is licensed under the [MIT License](LICENSE).
