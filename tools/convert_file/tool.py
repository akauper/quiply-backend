import re
import sys


def convert_field(field):
    field_name, field_type = field.split(":")
    field_name = re.sub(r"_(\w)", lambda m: m.group(1).upper(), field_name.strip())
    field_type = field_type.strip()

    if "Optional" in field_type:
        field_type = field_type.replace("Optional[", "").replace("]", "")
        field_name += "?"

    if field_type == "int":
        field_type = "number"
    elif field_type == "str":
        field_type = "string"
    elif field_type == "bool":
        field_type = "boolean"
    elif field_type == "float":
        field_type = "number"
    elif field_type.startswith("Dict["):
        key_type, value_type = re.findall(r"\[(.*?)\]", field_type)
        field_type = f"Record<{convert_type(key_type)}, {convert_type(value_type)}>"
    elif field_type == "list":
        field_type = "any[]"

    return f"  {field_name}: {field_type};"


def convert_type(type_str):
    if type_str == "str":
        return "string"
    elif type_str == "int":
        return "number"
    elif type_str == "bool":
        return "boolean"
    elif type_str == "float":
        return "number"
    else:
        return type_str


def convert_class(class_def):
    class_name = class_def.group(1)
    fields = class_def.group(2).split("\n")
    fields = [convert_field(field) for field in fields if field.strip()]

    return f"interface {class_name} {{\n{''.join(fields)}\n}}"


def convert_file(input_file, output_file):
    with open(input_file, "r") as file:
        content = file.read()

    pattern = re.compile(r"class (\w+)\(BaseModel\):\s*(.*?)(?=\n\s*(?:def|class|\Z))", re.DOTALL)
    converted_content = pattern.sub(convert_class, content)

    with open(output_file, "w") as file:
        file.write(converted_content)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_file(input_file, output_file)
