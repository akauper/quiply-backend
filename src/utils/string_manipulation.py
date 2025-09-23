import re
from typing import List
from .logging import logger


def str_to_seconds(time_str: str, default: int | None = None) -> int | None:
    if time_str is None or time_str == "" or time_str == "0" or time_str == "0 seconds":
        return default
    try:
        value_str, unit = time_str.split()
        value = int(value_str)
        unit = unit.lower()

        if unit in ['second', 'seconds']:
            return value
        elif unit in ['minute', 'minutes']:
            return value * 60
        elif unit in ['hour', 'hours']:
            return value * 3600
        else:
            logger.error(f"Invalid time unit: {unit}")
            return default
    except ValueError as e:
        logger.error(f"str_to_seconds Error: {e}")
        return default


def list_to_comma_delimited_str(items: List[str]) -> str:
    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return f"{', '.join(items[:-1])}, and {items[-1]}"


def add_tab_to_each_line(text: str, skip_first_line: bool = False) -> str:
    lines = text.splitlines()
    if skip_first_line:
        lines_with_tabs = [lines[0]] + ['\t' + line for line in lines[1:]]
    else:
        lines_with_tabs = ['\t' + line for line in lines]
    return '\n'.join(lines_with_tabs)


# def add_indent_to_each_line(text: str, indent: int, skip_first_line: bool = False) -> str:
#     lines = text.splitlines()
#     lines_with_tabs = [' ' * indent + line for line in lines]
#     return '\n'.join(lines_with_tabs)

def add_indent_to_each_line(text: str, indent: int, skip_first_line: bool = False) -> str:
    lines = text.splitlines()
    lines_with_tabs = []

    for i, line in enumerate(lines):
        if skip_first_line and i == 0:
            lines_with_tabs.append(line)
        else:
            lines_with_tabs.append(' ' * indent + line)

    return '\n'.join(lines_with_tabs)


def is_empty_string(s: str) -> bool:
    return re.fullmatch(r"\s*", s) is not None


def format_dict(d: dict, indent=0):
    formatted_str = ""

    # for k, v in d.items():
    #     formatted_str += '\n'

    for key, value in d.items():
        formatted_str += str(key) + ": {\n"
        if isinstance(value, dict):
            formatted_str += "\n" + format_dict(value, indent * 2)
        else:
            formatted_str += add_tab_to_each_line(str(value))
        formatted_str += '\n}\n'
        # formatted_str += ' ' * indent + str(key) + ": "
        # if isinstance(value, dict):
        #     formatted_str += "\n" + format_dict(value, indent + 2)
        # else:
        #     formatted_str += str(value) + "\n"
    return formatted_str
