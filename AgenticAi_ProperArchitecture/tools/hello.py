schema = {
    "type": "function",
    "function": {
        "name": "hello_world",
        "description": "Print Hello World.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

def execute():
    print("Hello World")
    return "Hello World executed."