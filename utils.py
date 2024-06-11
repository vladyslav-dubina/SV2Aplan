import re
from ast import literal_eval
from typing import List


class Color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    ORANGE = "\033[38;5;208m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def addSpacesAroundOperators(expression: str):
    operators = [
        r"\+",
        r"-",
        r"\*",
        r"/",
        r"%",
        r"\^",
        r"==",
        r"!=",
        r">=",
        r"<=",
        r">",
        r"<",
        r"&&",
        r"\|\|",
        r"!",
        r"&",
        r"\|",
        r"\(",
        r"\)",
    ]
    pattern = "|".join(operators)

    spaced_expression = re.sub(f"({pattern})", r" \1 ", expression)
    spaced_expression = re.sub(r"\s+", " ", spaced_expression).strip()

    return spaced_expression


def format_time(seconds):
    minutes = seconds // 60
    seconds %= 60

    if minutes > 0:
        return f"{int(minutes)} m {int(seconds)} s"
    else:
        return f"{int(seconds)} s"


def printWithColor(text, color_start: Color, color_end: Color = Color.END):
    print(color_start + text + color_end)


MODULE_COUNTER = 1


def generate_module_names():
    global MODULE_COUNTER
    module_name = "module_" + str(MODULE_COUNTER)
    MODULE_COUNTER += 1
    return module_name


def removeTrailingComma(s: str) -> str:
    return s.rstrip(",")


def valuesToAplanStandart(expression: str) -> str:
    values_patterns = [
        r"([0-9]+)\'(b)([01]+)",  # for binary
        r"([0-9]+)\'(h)([a-fA-F0-9]+)",  # for hex
    ]

    pattern = "|".join(values_patterns)

    def replace_match(match):
        print("----")
        for i in range(len(values_patterns)):
            multiplier = 0
            if i > 0:
                multiplier = 3 * (i)
            base, value_type, value_string = (
                match.group(1 + multiplier),
                match.group(2 + multiplier),
                match.group(3 + multiplier),
            )
            if base is not None:
                break
        if value_type == "h":
            value_string = "0x" + value_string
        elif value_type == "b":
            value_string = "0b" + value_string
        value = literal_eval(value_string)
        return str(value)

    expression = re.sub(pattern, lambda match: replace_match(match), expression)

    return expression


def addBracketsAfterTilda(expression: str):
    pattern = r"~([^\s]*)"
    result = re.sub(pattern, r"~(\1)", expression)
    return result


def parallelAssignment2Assignment(expression: str):
    pattern = r"<="
    result = re.sub(pattern, "=", expression)
    return result


def isInStrList(array: List[str], search_word: str):
    for element in array:
        if element == search_word:
            return True
    return False
