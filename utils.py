import re
import os
from ast import literal_eval
from classes.counters import Counters, CounterTypes
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.parametrs import ParametrArray


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
        r"=",
        r"\?",
        r":",
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


REMOVE_PRINTS = False


def switchRemovePrints(flag: bool):
    global REMOVE_PRINTS
    REMOVE_PRINTS = flag


def printWithColor(text, color_start: Color, color_end: Color = Color.END):
    if REMOVE_PRINTS == False:
        print(color_start + text + color_end)


Counters_Object = Counters()


def moduleCounterDeinit():
    global Counters_Object
    Counters_Object.countersDeinit()


def generate_module_names():
    global Counters_Object
    index = Counters_Object.getCounter(CounterTypes.MODULE_COUNTER)
    module_name = "module_" + str(index)
    Counters_Object.incrieseCounter(CounterTypes.MODULE_COUNTER)
    return (module_name, index)


def removeTrailingComma(s: str) -> str:
    return s.rstrip(",")


def valuesToAplanStandart(expression: str) -> str:
    values_patterns = [
        r"([0-9]+)\'(b)([01]+)",  # for binary
        r"([0-9]+)\'(h)([a-fA-F0-9]+)",  # for hex
        r"()(\')([0-9]+)",  # for '0
    ]

    pattern = "|".join(values_patterns)

    def replace_match(match):
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


def doubleOperators2Aplan(expression: str):
    patterns = [r"(\w+)(\+\+)", r"(\w+)(--)"]
    pattern = "|".join(patterns)

    def replace_match(match):
        for i in range(len(patterns)):
            if match.group(i) is not None:
                if i == 0:
                    value = f"{match.group(i+1)} = {match.group(i+1)} + 1"
                elif i == 1:
                    value = f"{match.group(i+1)} = {match.group(i+1)} - 1"
                else:
                    printWithColor(f"Unhandled case {match}", Color.RED)
                return value

        return value

    result = re.sub(pattern, lambda match: replace_match(match), expression)

    return result


def notConcreteIndex2AplanStandart(expression: str):
    pattern = r"(\w+\.\w+)\[([^\[\]]*[a-zA-Z][^\[\]]*)\]"

    def replace_match(match):
        identifier, index = match.group(1), match.group(2)
        return f"BGETI({identifier}, {index})"

    result = re.sub(pattern, lambda match: replace_match(match), expression)
    return result


def vectorSizes2AplanStandart(expression: str):
    patterns = [r"\[(\d+)\]", r"\[(\d+)\s*:\s*(\d+)\]"]

    pattern = "|".join(patterns)

    def replace_match(match):

        for i in range(len(patterns)):
            value_1, value_2 = (
                match.group(1 + i),
                match.group(2 + i),
            )
            if value_1 is not None:
                break
        if value_2 is None:
            value = f"({value_1},1)"
        else:
            value = f"({value_2},{value_1})"
        return value

    expression = re.sub(pattern, lambda match: replace_match(match), expression)

    return expression


def generatePythonStyleTernary(expression: str):
    pattern = (
        r"\((?P<condition>.+)\)\s*\?\s*(?P<true_value>.+)\s*:\s*(?P<false_value>.+)"
    )
    match = re.match(pattern, expression)

    if match:
        condition = match.group("condition")
        true_value = match.group("true_value")
        false_value = match.group("false_value")
        expression = f"({true_value} if {condition} else {false_value})"
        return expression
    else:
        return expression


def replace_cpp_operators(expression: str) -> str:
    replacements = {
        r"\b&&\b": "and",
        r"\b\|\|\b": "or",
        r"!": "not ",
        r"\btrue\b": "True",
        r"\bfalse\b": "False",
    }

    for cpp_op, py_op in replacements.items():
        expression = re.sub(cpp_op, py_op, expression)

    return expression


def vectorSize2AplanVectorSize(left, right):
    if right == "0":
        left = int(left) + 1
        return [left, 0]
    else:
        right = int(right)
        left = int(left)
        return [left - right, right]


def removeTypeFromForInit(ctx: SystemVerilogParser.For_initializationContext):
    result = ""
    for element in ctx.for_variable_declaration():
        result += f"{element.variable_identifier(0).getText()}"
        result += "="
        result += f"{element.expression(0).getText()}"
    return result


def evaluateExpression(expr: str):
    result = eval(expr)
    return result


def extractDimentionSize(s: str):
    matches = re.findall(r"\[\s*(.+)\s*\]", s)
    if matches:
        value = matches[0][0]
        value = evaluateExpression(value)
        return value


def extractVectorSize(s: str):
    matches = re.findall(r"\[(.+)\s*:\s*(.+)\]", s)
    if matches:
        left = matches[0][0]
        right = matches[0][1]
        left = evaluateExpression(left)
        right = evaluateExpression(right)
        result = [str(left), str(right)]
        return result


def is_numeric_string(s):
    match = re.fullmatch(r"\d+", s)
    return match.group(0) if match else None


def replaceParametrsCalls(param_array: ParametrArray, expression: str):
    for element in param_array.elements:
        expression = re.sub(
            r"\b{}\b".format(re.escape(element.identifier)),
            str(element.value),
            expression,
        )

    return expression


def replace_filename(path: str, new_filename: str) -> str:
    directory = os.path.dirname(path)
    new_path = os.path.join(directory, new_filename)
    return new_path
