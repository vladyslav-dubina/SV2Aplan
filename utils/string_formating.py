import re
import os
from utils.utils import printWithColor, Color
from ast import literal_eval
from classes.parametrs import ParametrArray


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


def addBracketsAfterNegation(expression: str):
    pattern = r"!([^\s]*)"
    result = re.sub(pattern, r"!(\1)", expression)
    return result


def replaceArrayIndexing(expression: str):
    pattern = r"\[(\w+)\]"
    result = re.sub(pattern, r"(\1)", expression)
    return result


def addLeftValueForUnaryOrOperator(expression: str):
    prefix = expression.split("=")[0].strip()

    pattern = re.compile(r"(?<![a-zA-Z0-9_])\|")

    new_expression = pattern.sub(f"{prefix}|", expression)

    return new_expression


def addBracketsAfterTilda(expression: str):
    pattern = r"~([^\s]*)"
    result = re.sub(pattern, r"~(\1)", expression)
    return result


def parallelAssignment2Assignment(expression: str):
    pattern = r"<="
    result = re.sub(pattern, "=", expression)
    return result


def addEqueToBGET(expression: str):
    pattern = r"(BGET\(.+\))"
    result = re.sub(pattern, r"\1 == 1", expression)
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


def notConcreteIndex2AplanStandart(expression: str, module):
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
