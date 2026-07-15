import os
import shutil
from pypdf import PdfReader
# -------------------------------------------------
# NOTE: each tool below follows the same pattern as
# software.py — a `schema` dict + an `execute()` fn.
# Your auto-discovery registry can pick these all up
# automatically since each has both attributes.
# -------------------------------------------------

MAX_READ_CHARS = 20000  # avoid dumping huge files into the LLM context


# =================================================
# 1. search_files
# =================================================

search_files_schema = {
    "type": "function",
    "function": {
        "name": "search_files",
        "description": "Search for files by name (substring match, case-insensitive) inside a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Text to search for in file names."},
                "directory": {"type": "string", "description": "Directory to search in."},
                "recursive": {"type": "boolean", "description": "Search subfolders too. Default true."}
            },
            "required": ["query", "directory"]
        }
    }
}

def search_files(query, directory, recursive=True):
    if not os.path.isdir(directory):
        return f"Directory not found: {directory}"

    query = query.lower()
    matches = []

    if recursive:
        for root, _, files in os.walk(directory):
            for f in files:
                if query in f.lower():
                    matches.append(os.path.join(root, f))
    else:
        for f in os.listdir(directory):
            full = os.path.join(directory, f)
            if os.path.isfile(full) and query in f.lower():
                matches.append(full)

    if not matches:
        return f"No files matching '{query}' found in {directory}."

    return "\n".join(matches[:50])  # cap output so huge matches don't flood context


# =================================================
# 2. read_file
# =================================================

read_file_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the text content of a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path to the file."}
            },
            "required": ["path"]
        }
    }
}
BINARY_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg", ".exe", ".zip"}
def read_file(path):
    if not os.path.isfile(path):
        return f"File not found: {path}"

    ext = os.path.splitext(path)[1].lower()
    if ext in BINARY_EXTENSIONS:
        return f"'{path}' is a binary file and can't be read as text. Use read_pdf for PDFs."
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read(MAX_READ_CHARS + 1)

        if len(content) > MAX_READ_CHARS:
            content = content[:MAX_READ_CHARS] + "\n...[truncated]"

        return content if content.strip() else "(File is empty.)"

    except Exception as e:
        return f"Failed to read {path}: {e}"


# =================================================
# 3. write_file
# =================================================

write_file_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write text content to a file. Creates the file (and parent folders) if it doesn't exist. Overwrites existing content.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path to the file."},
                "content": {"type": "string", "description": "Text content to write."}
            },
            "required": ["path", "content"]
        }
    }
}

def write_file(path, content):
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {len(content)} characters to {path}."

    except Exception as e:
        return f"Failed to write {path}: {e}"


# =================================================
# 4. create_folder
# =================================================

create_folder_schema = {
    "type": "function",
    "function": {
        "name": "create_folder",
        "description": "Create a new folder (and any missing parent folders).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path of the folder to create."}
            },
            "required": ["path"]
        }
    }
}

def create_folder(path):
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created (or already existed): {path}"

    except Exception as e:
        return f"Failed to create folder {path}: {e}"


# =================================================
# 5. move_file
# =================================================

move_file_schema = {
    "type": "function",
    "function": {
        "name": "move_file",
        "description": "Move a file (or folder) from one location to another.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "description": "Current path of the file/folder."},
                "destination": {"type": "string", "description": "Destination path."}
            },
            "required": ["source", "destination"]
        }
    }
}

def move_file(source, destination):
    if not os.path.exists(source):
        return f"Source not found: {source}"

    try:
        shutil.move(source, destination)
        return f"Moved {source} -> {destination}"

    except Exception as e:
        return f"Failed to move {source}: {e}"


# =================================================
# 6. rename_file
# =================================================

rename_file_schema = {
    "type": "function",
    "function": {
        "name": "rename_file",
        "description": "Rename a file or folder in place (keeps it in the same directory).",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path of the file/folder to rename."},
                "new_name": {"type": "string", "description": "New name (not a full path, just the name)."}
            },
            "required": ["path", "new_name"]
        }
    }
}

def rename_file(path, new_name):
    if not os.path.exists(path):
        return f"Path not found: {path}"

    try:
        directory = os.path.dirname(path)
        new_path = os.path.join(directory, new_name)
        os.rename(path, new_path)
        return f"Renamed {path} -> {new_path}"

    except Exception as e:
        return f"Failed to rename {path}: {e}"


# =================================================
# 7. delete_file
# =================================================

delete_file_schema = {
    "type": "function",
    "function": {
        "name": "delete_file",
        "description": "Permanently delete a file. This cannot be undone — use with caution.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path of the file to delete."}
            },
            "required": ["path"]
        }
    }
}

def delete_file(path):
    if not os.path.isfile(path):
        return f"File not found: {path}"

    try:
        #os.remove(path)
        return f"Man i dont want to risk it delete yourself: {path}"

    except Exception as e:
        return f"Failed to delete {path}: {e}"



MAX_PDF_CHARS = 6000  # keep well under your context window

read_pdf_schema = {
    "type": "function",
    "function": {
        "name": "read_pdf",
        "description": "Extract and read the text content of a PDF file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path to the PDF file."}
            },
            "required": ["path"]
        }
    }
}

def read_pdf(path):
    if not os.path.isfile(path):
        return f"File not found: {path}"
    if not path.lower().endswith(".pdf"):
        return f"Not a PDF file: {path}"

    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        if not text.strip():
            return "No extractable text found (this may be a scanned/image-based PDF)."

        if len(text) > MAX_PDF_CHARS:
            text = text[:MAX_PDF_CHARS] + "\n...[truncated — file is longer]"

        return text

    except Exception as e:
        return f"Failed to read PDF {path}: {e}"
# =================================================
# 8. list_directory
# =================================================

list_directory_schema = {
    "type": "function",
    "function": {
        "name": "list_directory",
        "description": "List the folders and files inside a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Full path of the directory to list."}
            },
            "required": ["path"]
        }
    }
}

def list_directory(path):
    if not os.path.isdir(path):
        return f"Directory not found: {path}"

    try:
        entries = os.listdir(path)
        folders = sorted(e for e in entries if os.path.isdir(os.path.join(path, e)))
        files = sorted(e for e in entries if os.path.isfile(os.path.join(path, e)))

        result = "Folders:\n" + ("\n".join(folders) if folders else "(none)")
        result += "\n\nFiles:\n" + ("\n".join(files) if files else "(none)")
        return result

    except Exception as e:
        return f"Failed to list {path}: {e}"


# =================================================
# Bundle for auto-discovery
# (registry can grab TOOLS_IN_MODULE if it collects
#  multiple tools per file instead of one)
# =================================================

TOOLS_IN_MODULE = {
    "search_files": (search_files_schema, search_files),
    "read_file": (read_file_schema, read_file),
    "write_file": (write_file_schema, write_file),
    "create_folder": (create_folder_schema, create_folder),
    "move_file": (move_file_schema, move_file),
    "rename_file": (rename_file_schema, rename_file),
    "delete_file": (delete_file_schema, delete_file),
    "list_directory": (list_directory_schema, list_directory),
       "read_pdf": (read_pdf_schema, read_pdf)
}
