from tools import calculator
from tools import hello

TOOLS = {
    "open_calculator": calculator.execute,
    "hello_world": hello.execute,
}

SCHEMAS = [
    calculator.schema,
    hello.schema
]