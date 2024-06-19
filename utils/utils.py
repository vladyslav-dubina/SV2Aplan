import re

from typing import Tuple, List

from classes.counters import Counters, CounterTypes
from antlr4_verilog.systemverilog import SystemVerilogParser


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


def printWithColors(
    input: List[Tuple[str, Color]],
):
    if REMOVE_PRINTS == False:
        color_end = Color.END
        print_str = ""
        for element in input:
            text, color_start = element
            print_str += color_start + text + color_end
        print(print_str)


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
