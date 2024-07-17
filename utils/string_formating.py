import re
import os
from utils.utils import printWithColor, Color
from ast import literal_eval
from classes.parametrs import ParametrArray


def addSpacesAroundOperators(expression: str):
    """The function `addSpacesAroundOperators` adds spaces around operators in a given input expression.

    Parameters
    ----------
    expression : str
        The `addSpacesAroundOperators` function takes an input expression as a string and adds spaces
    around operators in the expression. This makes the expression more readable and easier to parse.

    Returns
    -------
        The `addSpacesAroundOperators` function returns the input expression with spaces added around the
    operators specified in the `operators` list.

    """
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


def removeTrailingComma(s: str) -> str:
    """The function `removeTrailingComma` takes a string as input and removes any trailing commas from the
    end of the string.

    Parameters
    ----------
    s : str
        The parameter `s` in the `removeTrailingComma` function is a string (`str`). This function is
    designed to remove any trailing commas from the input string.

    Returns
    -------
        The function `removeTrailingComma` is returning the input string `s` with any trailing commas
    removed.

    """
    return s.rstrip(",")


def valuesToAplanStandart(expression: str) -> str:
    """The function `valuesToAplanStandart` converts values in different number systems to their standard
    representation.

    Parameters
    ----------
    expression : str
        The function `valuesToAplanStandart` takes an input expression as a string and converts any values
    specified in non-standard formats to their standard representation. The function uses regular
    expressions to identify different value patterns such as binary, hexadecimal, and decimal values.

    Returns
    -------
        The function `valuesToAplanStandart` takes an input expression as a string and processes it to
    convert any values specified in non-standard formats to standard integer values. The function uses
    regular expressions to identify different patterns for binary, hexadecimal, and decimal values. It
    then converts these values to standard integer format and returns the modified input expression as a
    string.

    """
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


def addBracketsAfterNegation(expression: str):
    """The function `addBracketsAfterNegation` adds brackets after the negation symbol `!` in a given input
    expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `addBracketsAfterNegation` returns the input expression with brackets added after the
    negation symbol `!`.

    """
    pattern = r"!([^\s]*)"
    result = re.sub(pattern, r"!(\1)", expression)
    return result


def replaceArrayIndexing(expression: str):
    """The function `replaceArrayIndexing` replaces square brackets used for array indexing with
    parentheses in a given input expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `replaceArrayIndexing` takes an input expression as a string, replaces square brackets
    `[]` with parentheses `()` around the index value, and returns the modified expression.

    """
    pattern = r"\[(\w+)\]"
    result = re.sub(pattern, r"(\1)", expression)
    return result


def addLeftValueForUnaryOrOperator(expression: str):
    """The function adds a left value for a unary or operator in a given input expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `addLeftValueForUnaryOrOperator` returns a modified version of the input expression
    where a prefix is added before any occurrence of the `|` operator that is not preceded by a letter,
    number, or underscore.

    """
    prefix = expression.split("=")[0].strip()

    pattern = re.compile(r"(?<![a-zA-Z0-9_])\|")

    new_expression = pattern.sub(f"{prefix}|", expression)

    return new_expression


def addBracketsAfterTilda(expression: str):
    """The function `addBracketsAfterTilda` adds brackets `()` after the tilde `~` in a given input
    expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `addBracketsAfterTilda` takes an input expression as a string and adds brackets `()`
    after the tilde `~` symbol. The function uses a regular expression pattern to match the tilde
    followed by any non-space characters and then replaces it with the tilde followed by the matched
    non-space characters enclosed in brackets.

    """
    pattern = r"~([^\s]*)"
    result = re.sub(pattern, r"~(\1)", expression)
    return result


def parallelAssignment2Assignment(expression: str):
    """The function `parallelAssignment2Assignment` replaces the "<=" operator with "=" in a given input
    expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `parallelAssignment2Assignment` takes an input expression as a string, searches for
    the pattern `<=` in the expression, and replaces it with `=`. The modified expression is then
    returned.

    """
    pattern = r"<="
    result = re.sub(pattern, "=", expression)
    return result


def addEqueToBGET(expression: str):
    """The function `addEqueToBGET` takes an input expression, searches for the pattern "BGET(...)" within
    the expression, and replaces it with "BGET(...) == 1".

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `addEqueToBGET` takes an input expression as a string, searches for any occurrences of
    the pattern "BGET(...)" using regular expressions, and replaces them with "BGET(...) == 1". The
    modified expression is then returned.

    """
    pattern = r"(BGET\(.+\))"
    result = re.sub(pattern, r"\1 == 1", expression)
    return result


def doubleOperators2Aplan(expression: str):
    """The function `doubleOperators2Aplan` takes an input expression as a string and replaces increment
    and decrement operators with their corresponding assignment operations.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The `doubleOperators2Aplan` function takes an input expression as a string and looks for patterns
    of increment (++) and decrement (--) operators applied to variables. It then replaces these patterns
    with the corresponding increment or decrement assignment statements. The modified expression is
    returned as the result.

    """
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


def notConcreteIndex2AplanStandart(expression: str, module):
    """The function `notConcreteIndex2AplanStandart` takes an expression and a module, and replaces
    specific index references with function calls based on the module's declarations.

    Parameters
    ----------
    expression : str
        The `expression` parameter is a string that represents an expression containing array accesses in
    the format `identifier[index]`. The function `notConcreteIndex2AplanStandart` is designed to modify
    these array accesses based on certain conditions.
    module
        The `module` parameter in the `notConcreteIndex2AplanStandart` function is expected to be an object
    that contains declarations with dimensions. The function uses this module to find a declaration with
    a dimension by name and then performs a specific replacement in the given expression based on the
    match found.

    Returns
    -------
        The function `notConcreteIndex2AplanStandart` takes an expression and a module as input parameters.
    It searches for a specific pattern in the expression, where a word followed by a dot and another
    word is followed by square brackets containing an index.

    """
    pattern = r"(\w+\.\w+)\[([^\[\]]*[a-zA-Z][^\[\]]*)\]"

    def replace_match(match):
        identifier, index = match.group(1), match.group(2)
        tmp = identifier.split(".")
        decl_with_dimention = module.declarations.findDeclWithDimentionByName(tmp[1])
        if decl_with_dimention is not None:
            return f"{identifier}({index})"
        else:
            return f"BGET({identifier}, {index})"

    result = re.sub(pattern, lambda match: replace_match(match), expression)
    return result


def vectorSizes2AplanStandart(expression: str):
    """The function `vectorSizes2AplanStandart` in the provided Python code snippet converts vector size
    expressions to a standard format.

    Parameters
    ----------
    expression : str
        The function `vectorSizes2AplanStandart` takes an expression as input and processes it based on
    certain patterns defined in the function. The patterns are used to identify specific formats within
    the expression, such as `[x]` or `[x:y]`, where `x` and `y`

    Returns
    -------
        The function `vectorSizes2AplanStandart` takes an input `expression` as a string and processes it
    based on certain patterns related to vector sizes. It uses regular expressions to match patterns
    like `[number]` or `[number : number]` and then replaces them with a modified format. The function
    then returns the modified expression.

    """
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
            value = f"({value_1})"
        else:
            value = f"({value_2},{value_1})"
        return value

    expression = re.sub(pattern, lambda match: replace_match(match), expression)

    return expression


def generatePythonStyleTernary(expression: str):
    """The function `generatePythonStyleTernary` converts a ternary expression in a specific format to
    Python ternary operator format.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The `generatePythonStyleTernary` function returns a Python-style ternary expression based on the
    input expression provided. If the input expression matches the ternary pattern, it converts it into
    a Python ternary expression format and returns it. Otherwise, it returns the original input
    expression.

    """
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
    """The function `replace_cpp_operators` converts C++ logical and arithmetic operators to their Python
    equivalents in a given expression.

    Parameters
    ----------
    expression : str

    Returns
    -------
        The function `replace_cpp_operators` takes a string `expression` as input and replaces C++
    operators with their Python equivalents using regular expressions. The function then returns the
    modified expression with C++ operators replaced by Python operators.

    """
    replacements = {
        r"&&": " and ",
        r"\|\|": " or ",
        r"!": " not ",
        r"(?<!/)/(?!/)": " // ",
        r"\btrue\b": " True ",
        r"\bfalse\b": " False ",
        r"\+\+": " += 1",
    }

    for cpp_op, py_op in replacements.items():
        expression = re.sub(cpp_op, py_op, expression)

    return expression


def replaceParametrsCalls(param_array: ParametrArray, expression: str):
    """The function `replaceParametrsCalls` replaces parameter calls in an expression with their
    corresponding values from a `ParametrArray`.

    Parameters
    ----------
    param_array : ParametrArray
        A `ParametrArray` is a data structure that contains elements representing parameters with
    identifiers and values. The `replaceParametrsCalls` function takes a `param_array` and an
    `expression` as input. It iterates over the elements in the `param_array` and replaces occurrences
    of the
    expression : str
        The `replaceParametrsCalls` function takes in a `ParametrArray` object and a string `expression`.
    It iterates through the elements in the `param_array` and replaces occurrences of the element's
    identifier in the `expression` with the element's value.

    Returns
    -------
        The function `replaceParametrsCalls` returns the modified `expression` string after replacing the
    identifiers with their corresponding values from the `param_array`.

    """
    for element in param_array.elements:
        expression = re.sub(
            r"\b{}\b".format(re.escape(element.identifier)),
            str(element.value),
            expression,
        )

    return expression


def replace_filename(path: str, new_filename: str) -> str:
    """The function `replace_filename` takes a file path and a new filename, and returns a new path with
    the updated filename.

    Parameters
    ----------
    path : str
        The `path` parameter is a string representing the file path of the original file including the
    filename.
    new_filename : str
        The `new_filename` parameter is a string that represents the new filename that you want to use for
    the file in the given `path`.

    Returns
    -------
        The function `replace_filename` returns a new path with the updated filename.

    """
    directory = os.path.dirname(path)
    new_path = os.path.join(directory, new_filename)
    return new_path
