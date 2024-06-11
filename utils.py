import re
from ast import literal_eval
from typing import List


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ORANGE = '\033[38;5;208m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def addSpacesAroundOperators(expression: str):
    operators = [
        r'\+', r'-', r'\*', r'/', r'%', r'\^',
        r'==', r'!=', r'>=', r'<=', r'>', r'<',
        r'&&', r'\|\|', r'!', r'&', r'\|',
        r'\(', r'\)',
    ]
    pattern = '|'.join(operators)

    spaced_expression = re.sub(f'({pattern})', r' \1 ', expression)
    spaced_expression = re.sub(r'\s+', ' ', spaced_expression).strip()

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
    module_name = 'module_' + str(MODULE_COUNTER)
    MODULE_COUNTER += 1
    return module_name


def removeTrailingComma(s: str) -> str:
    return s.rstrip(',')


def valuesToAplanStandart(expression: str):
    values_paterns = [r'([0-9]+)\'(b)([0-9]+)', r'([0-9]+)\'(h)([a-zA-Z0-9]+)']

    pattern = '|'.join(values_paterns)
    expression_search = re.search(pattern, expression)
    if (expression_search is not None):
        base, value_type, hex_string = expression_search.group(
            1), expression_search.group(2), expression_search.group(3)
        if (base is None or value_type is None or hex_string is None):
            base, value_type, hex_string = expression_search.group(
                4), expression_search.group(5), expression_search.group(6)
        if (value_type == 'h'):
            hex_string = '0x' + hex_string
        value = literal_eval(hex_string)
        expression = re.sub(f'({pattern})', str(value), expression)
    return expression

def addBracketsAfterTilda(expression: str):
   pattern = r'~([^\s]*)'
   result = re.sub(pattern, r'~(\1)', expression)
   return result 

def isInStrList(array: List[str], search_word: str):
    for element in array:
        if element == search_word:
            return True
    return False
