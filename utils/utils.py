import re
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Tuple, List

from classes.counters import Counters, CounterTypes
from antlr4_verilog.systemverilog import SystemVerilogParser


# The class `Color` defines various ANSI escape sequences for text color and formatting in Python.
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
    """The `format_time` function in Python converts a given number of seconds into a formatted string
    representing minutes and seconds.

    Parameters
    ----------
    seconds
        The `format_time` function takes a number of seconds as input and converts it into a formatted
    string representing the time in minutes and seconds.

    Returns
    -------
        The `format_time` function takes a number of seconds as input and converts it into a formatted
    string representing the time in minutes and seconds. If the input is greater than 60 seconds, it
    will return a string in the format "X m Y s" where X is the number of minutes and Y is the number of
    remaining seconds. If the input is less than 60 seconds, it will

    """
    minutes = seconds // 60
    seconds %= 60

    if minutes > 0:
        return f"{int(minutes)} m {int(seconds)} s"
    else:
        return f"{int(seconds)} s"


# The line `REMOVE_PRINTS = False` is initializing a global variable `REMOVE_PRINTS` with a boolean
# value of `False`. This variable is used in the code to control whether or not certain print
# statements should be executed. If `REMOVE_PRINTS` is set to `True`, the print statements in the code
# will be skipped, effectively suppressing any output that would have been printed to the console.
# This can be useful for toggling debug or informational output on or off in the codebase.
REMOVE_PRINTS = False


def switchRemovePrints(flag: bool):
    """The function `switchRemovePrints` sets a global variable `REMOVE_PRINTS` based on the input boolean
    flag.

    Parameters
    ----------
    flag : bool
        The `flag` parameter in the `switchRemovePrints` function is a boolean value that determines
    whether to enable or disable the removal of print statements in the code. When `flag` is set to
    `True`, the `REMOVE_PRINTS` global variable is set to `True`, indicating that

    """
    global REMOVE_PRINTS
    REMOVE_PRINTS = flag


def printWithColor(text, color_start: Color, color_end: Color = Color.END):
    """The function `printWithColor` prints the given text with specified color formatting.

    Parameters
    ----------
    text
        The `text` parameter is the string that you want to print with color formatting.
    color_start : Color
        The `color_start` parameter is used to specify the color code or formatting to be applied at the
    beginning of the text when it is printed. It is typically used to start the color or formatting
    effect.
    color_end : Color
        The `color_end` parameter is a Color enum that specifies the color code or formatting to end the
    colored text. It is optional and defaults to `Color.END`, which typically signifies the end of the
    colored text and resets the color to the default.

    """
    if REMOVE_PRINTS == False:
        print(color_start + text + color_end)


def printWithColors(
    input: List[Tuple[str, Color]],
):
    """The function `printWithColors` takes a list of tuples containing text and color information, and
    prints the text with the specified colors.

    Parameters
    ----------
    input : List[Tuple[str, Color]]
        The `printWithColors` function takes a list of tuples as input. Each tuple contains a string and a
    color. The function then concatenates the strings with the corresponding colors and prints the
    result.

    """
    if REMOVE_PRINTS == False:
        color_end = Color.END
        print_str = ""
        for element in input:
            text, color_start = element
            print_str += color_start + text + color_end
        print(print_str)


# `Counters_Object = Counters()` is initializing an instance of the `Counters` class and assigning it
# to the variable `Counters_Object`. This instance allows access to the methods and attributes defined
# within the `Counters` class. The `Counters` class likely contains functionality related to counting
# and tracking certain elements or metrics within the program.
Counters_Object = Counters()


def programCountersDeinit():
    """The function `programCountersDeinit` deinitializes the counters in the `Counters_Object`."""
    global Counters_Object
    Counters_Object.countersDeinit()


def vectorSize2AplanVectorSize(left: str | int | None, right: str | int | None):
    """The function `vectorSize2AplanVectorSize` takes two inputs, left and right, and returns a list with
    the difference between left and right as the first element and right as the second element, unless
    right is "0" in which case left is incremented by 1 and right is set to 0.

    Parameters
    ----------
    left
        The `left` parameter in the `vectorSize2AplanVectorSize` function represents the x-coordinate of a
    vector in a 2D plane.
    right
        The `right` parameter in the `vectorSize2AplanVectorSize` function represents the second component
    of a 2D vector. If `right` is equal to "0", the function increments the first component (`left`) by
    1 and sets the second component to 0. Otherwise

    Returns
    -------
        The function `vectorSize2AplanVectorSize` returns a list containing two elements. The first element
    is the result of subtracting the integer value of `right` from the integer value of `left` if
    `right` is not equal to "0". If `right` is equal to "0", the first element is the integer value of
    `left` incremented by 1. The

    """
    if left is None or right is None:
        printWithColor("ERROR! One of vector size values is None!", Color.RED)
        raise ValueError

    if right == "0":
        left = int(left) + 1
        return [left, 0]
    else:
        right = int(right)
        left = int(left)
        return [left - right, right]


def evaluateExpression(expr: str, variables=None):
    """The function `evaluateExpression` takes a string representing a mathematical expression, evaluates
    it, and returns the result.

    Parameters
    ----------
    expr : str
        The `evaluateExpression` function takes a string `expr` as input, which represents a mathematical
    expression that can be evaluated using the `eval` function in Python. The function then returns the
    result of evaluating the expression.

    Returns
    -------
        The function `evaluateExpression` takes a string `expr` as input, evaluates the expression using
    the `eval` function, and returns the result of the evaluation.

    """
    if variables is None:
        variables = {}
    result = eval(expr, {}, variables)
    return result


def extractDimentionSize(expression: str):
    if expression == "[$]":
        return
    matches = re.findall(r"\[\s*(.+)\s*\]", expression)
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


def isNumericString(s):
    match = re.fullmatch(r"\d+", s)
    return match.group(0) if match else None


def containsOperator(s):
    match = re.search(r"[+\-*/&|^~<>=%!]", s)
    return match.group(0) if match else None


def containsOnlyPipe(s):
    match = re.fullmatch(r"\|", s)
    return True if match else None


def isVariablePresent(expression: str, variable: str) -> bool:
    if len(variable) < 1:
        return False
    pattern = rf"\b{re.escape(variable)}\b"
    return re.search(pattern, expression) is not None


def extractFunctionName(expression: str) -> str:
    """
    Extracts the function name from a given expression.

    Parameters
    ----------
    expression : str
        The input string containing the function call.

    Returns
    -------
    str
        The name of the function if found, otherwise an empty string.
    """
    pattern = r"\b([\w$]+)\s*\("
    match = re.search(pattern, expression)
    if match:
        return match.group(1)
    return None


def dataTypeToStr(
    ctx: SystemVerilogParser.Data_typeContext,
):
    result = None
    if ctx.integer_vector_type() is not None:
        result = ctx.integer_vector_type().getText()
    elif ctx.signing() is not None:
        result = ctx.signing().getText()
    elif ctx.integer_atom_type() is not None:
        result = ctx.integer_atom_type().getText()
    elif ctx.non_integer_type() is not None:
        result = ctx.non_integer_type().getText()
    elif ctx.struct_union() is not None:
        result = ctx.struct_union().getText()
    elif ctx.interface_identifier() is not None:
        result = ctx.interface_identifier().getText()
    elif ctx.parameter_value_assignment() is not None:
        result = ctx.parameter_value_assignment().getText()
    elif ctx.modport_identifier() is not None:
        result = ctx.modport_identifier().getText()
    elif ctx.type_identifier() is not None:
        result = ctx.type_identifier().getText()
    elif ctx.type_identifier() is not None:
        result = ctx.type_identifier().getText()
    return result
