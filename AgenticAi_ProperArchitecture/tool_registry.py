from tools import filesystem, desktop_control, terminal, software,memory_tool

TOOLS = {}
SCHEMAS = []

for module in [filesystem, desktop_control, terminal,memory_tool]:
    for name, (schema, fn) in module.TOOLS_IN_MODULE.items():
        TOOLS[name] = fn
        SCHEMAS.append(schema)

# software.py still uses the single schema/execute pattern
TOOLS["open_software"] = software.execute
SCHEMAS.append(software.schema)