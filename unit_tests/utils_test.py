import pytest
import sys
import os
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.utils import (
    evaluateExpression,
    extractDimentionSize,
    extractFunctionName,
    extractVectorSize,
    format_time,
    isNumericString,
    isVariablePresent,
    vectorSize2AplanVectorSize,
)


# ================================= FORMAT_TIME ======================================
def test_format_time():
    # Test cases for format_time function
    assert format_time(0) == "0 s"
    assert format_time(30) == "30 s"
    assert format_time(60) == "1 m 0 s"
    assert format_time(61) == "1 m 1 s"
    assert format_time(120) == "2 m 0 s"
    assert format_time(121) == "2 m 1 s"
    assert format_time(3599) == "59 m 59 s"
    assert format_time(3600) == "60 m 0 s"


def test_format_time_invalid():
    # Test cases for invalid inputs (negative and non-integer values)
    with pytest.raises(TypeError):
        format_time("60")
    with pytest.raises(TypeError):
        format_time([60])
    with pytest.raises(TypeError):
        format_time(None)


# ======================= VECTOR_SIZE_2_APLAN_VECTOR_SIZE ==============================


def test_vectorSize2AplanVectorSize_zero_right():
    assert vectorSize2AplanVectorSize("3", "0") == [4, 0]
    assert vectorSize2AplanVectorSize("0", "0") == [1, 0]
    assert vectorSize2AplanVectorSize("-1", "0") == [0, 0]


def test_vectorSize2AplanVectorSize_non_zero_right():
    assert vectorSize2AplanVectorSize("5", "2") == [3, 2]
    assert vectorSize2AplanVectorSize("10", "3") == [7, 3]
    assert vectorSize2AplanVectorSize("7", "7") == [0, 7]
    assert vectorSize2AplanVectorSize("-3", "4") == [-7, 4]


def test_vectorSize2AplanVectorSize_left_zero():
    assert vectorSize2AplanVectorSize("0", "5") == [-5, 5]
    assert vectorSize2AplanVectorSize("0", "0") == [1, 0]


def test_vectorSize2AplanVectorSize_negative_values():
    assert vectorSize2AplanVectorSize("-5", "2") == [-7, 2]
    assert vectorSize2AplanVectorSize("5", "-2") == [7, -2]
    assert vectorSize2AplanVectorSize("-5", "-5") == [0, -5]


def test_vectorSize2AplanVectorSize_invalid_inputs():
    with pytest.raises(ValueError):
        vectorSize2AplanVectorSize("five", "2")
    with pytest.raises(ValueError):
        vectorSize2AplanVectorSize("5", "two")
    with pytest.raises(ValueError):
        vectorSize2AplanVectorSize("five", "two")
    with pytest.raises(ValueError):
        vectorSize2AplanVectorSize(None, "5")
    with pytest.raises(ValueError):
        vectorSize2AplanVectorSize("5", None)


# ============================ EVALUATE_EXPRESSION ==================================


def test_evaluateExpression_basic_math():
    assert evaluateExpression("1 + 1") == 2
    assert evaluateExpression("2 * 3") == 6
    assert evaluateExpression("10 / 2") == 5
    assert evaluateExpression("7 - 4") == 3


def test_evaluateExpression_with_parentheses():
    assert evaluateExpression("(1 + 2) * 3") == 9
    assert evaluateExpression("10 / (2 + 3)") == 2


def test_evaluateExpression_with_variables():
    variables = {"a": 10, "b": 5}
    assert evaluateExpression("a + b", variables) == 15
    assert evaluateExpression("a * b", variables) == 50


def test_evaluateExpression_with_complex_expressions():
    assert evaluateExpression("2 ** 3") == 8
    assert evaluateExpression("max(1, 2, 3)") == 3


def test_evaluateExpression_invalid_input():
    with pytest.raises(ZeroDivisionError):
        evaluateExpression("1 / 0")
    with pytest.raises(NameError):
        evaluateExpression("undefined_variable + 1")
    with pytest.raises(SyntaxError):
        evaluateExpression("1 + (2 * 3")


# ============================ EXTRACT_DIMENTION_SIZE ==================================


@patch("utils.utils.evaluateExpression")
def test_extractDimentionSize_basic(mock_evaluateExpression):
    mock_evaluateExpression.return_value = 5

    assert extractDimentionSize("array[5]") == 5
    assert extractDimentionSize("array[ 2 + 3 ]") == 5


@patch("utils.utils.evaluateExpression")
def test_extractDimentionSize_multiple_brackets(mock_evaluateExpression):
    mock_evaluateExpression.return_value = 7

    assert extractDimentionSize("array[7]") == 7
    assert extractDimentionSize("matrix[3 + 4]") == 7


@patch("utils.utils.evaluateExpression")
def test_extractDimentionSize_no_brackets(mock_evaluateExpression):
    mock_evaluateExpression.return_value = 0

    assert extractDimentionSize("array") is None
    assert extractDimentionSize("array[]") is None


@patch("utils.utils.evaluateExpression")
def test_extractDimentionSize_invalid_expression(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = ZeroDivisionError()

    with pytest.raises(ZeroDivisionError):
        extractDimentionSize("array[1 / 0]")

    mock_evaluateExpression.side_effect = NameError("Name not defined")

    with pytest.raises(NameError):
        extractDimentionSize("array[undefined_var]")

    assert extractDimentionSize("array[1 + (2 * 3") is None


# ============================ EXTRACT_VECTOR_SIZE ==================================


@patch("utils.utils.evaluateExpression")
def test_extractVectorSize_basic(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = [
        3,
        7,
    ]  # Define the results for each evaluateExpression call

    result = extractVectorSize("vector[3 : 7]")
    assert result == ["3", "7"]


@patch("utils.utils.evaluateExpression")
def test_extractVectorSize_with_spaces(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = [
        10,
        20,
    ]  # Define the results for each evaluateExpression call

    result = extractVectorSize("vector[ 10 : 20 ]")
    assert result == ["10", "20"]


@patch("utils.utils.evaluateExpression")
def test_extractVectorSize_no_colon(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = [
        0,
        0,
    ]  # Define the results for each evaluateExpression call

    result = extractVectorSize("vector[0:0]")
    assert result == ["0", "0"]


@patch("utils.utils.evaluateExpression")
def test_extractVectorSize_empty_string(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = [
        0,
        0,
    ]  # Define the results for each evaluateExpression call

    result = extractVectorSize("vector[]")
    assert result is None


@patch("utils.utils.evaluateExpression")
def test_extractVectorSize_invalid_expression(mock_evaluateExpression):
    mock_evaluateExpression.side_effect = ZeroDivisionError()

    with pytest.raises(ZeroDivisionError):
        extractVectorSize("vector[1 / 0 : 2]")

    mock_evaluateExpression.side_effect = NameError("Name not defined")

    with pytest.raises(NameError):
        extractVectorSize("vector[undefined_var : 2]")

    assert extractDimentionSize("vector[1 + (2 * 3 : 4") is None


# ============================ IS_NUMERIC_STRING ==================================


def test_isNumericString_basic():
    assert isNumericString("12345") == "12345"
    assert isNumericString("0") == "0"


def test_isNumericString_with_non_numeric_characters():
    assert isNumericString("123a") is None
    assert isNumericString("abc") is None
    assert isNumericString("123 456") is None


def test_isNumericString_empty_string():
    assert isNumericString("") is None


def test_isNumericString_with_special_characters():
    assert isNumericString("123!") is None
    assert isNumericString("123#") is None


def test_isNumericString_with_leading_trailing_spaces():
    assert isNumericString(" 123 ") is None
    assert isNumericString("123 ") is None
    assert isNumericString(" 123") is None


# ============================ IS_VARIABLE_PRESENT ==================================


def test_isVariablePresent_basic():
    assert isVariablePresent("x + y", "x") is True
    assert isVariablePresent("x + y", "y") is True


def test_isVariablePresent_with_multiple_occurrences():
    assert isVariablePresent("x + x + y", "x") is True
    assert isVariablePresent("a = x + y * x", "x") is True
    assert isVariablePresent("a = x + y * x", "y") is True


def test_isVariablePresent_with_variables_surrounded_by_operators():
    assert isVariablePresent("a + (x * y) - z", "x") is True
    assert isVariablePresent("a + (x * y) - z", "y") is True
    assert isVariablePresent("a + (x * y) - z", "z") is True


def test_isVariablePresent_with_edge_cases():
    assert isVariablePresent("abc", "abc") is True
    assert isVariablePresent("abc123", "abc") is False
    assert isVariablePresent("123abc", "abc") is False


def test_isVariablePresent_with_special_characters():
    assert isVariablePresent("a_variable = 10", "a_variable") is True
    assert isVariablePresent("variable_1 = 10", "variable_1") is True
    assert isVariablePresent("var1 = 10", "var1") is True
    assert isVariablePresent("var1 = 10", "var") is False


def test_isVariablePresent_with_substrings():
    assert isVariablePresent("variable", "var") is False
    assert isVariablePresent("variable", "variable") is True
    assert isVariablePresent("var", "variable") is False


def test_isVariablePresent_empty_expression():
    assert isVariablePresent("", "x") is False


def test_isVariablePresent_empty_variable():
    assert isVariablePresent("some text", "") is False


# ============================ EXTRACT_FUNCTION_NAME ==================================
def test_extractFunctionName_name_basic():
    expression = "foo(bar, baz)"
    result = extractFunctionName(expression)
    assert result == "foo"


def test_extractFunctionName_name_with_spaces():
    expression = " foo ( bar, baz ) "
    result = extractFunctionName(expression)
    assert result == "foo"


def test_extractFunctionName_name_with_tabs():
    expression = "foo\t(\tbar,\tbaz\t)"
    result = extractFunctionName(expression)
    assert result == "foo"


def test_extractFunctionName_name_with_newlines():
    expression = "foo\n(\nbar,\nbaz\n)"
    result = extractFunctionName(expression)
    assert result == "foo"


def test_extractFunctionName_name_empty():
    expression = ""
    result = extractFunctionName(expression)
    assert result is None


def test_extractFunctionName_name_no_function():
    expression = "bar baz"
    result = extractFunctionName(expression)
    assert result is None


def test_extractFunctionName_name_with_numbers():
    expression = "foo123(bar, baz)"
    result = extractFunctionName(expression)
    assert result == "foo123"


def test_extractFunctionName_name_multiple_functions():
    expression = "foo(bar, baz) + bar(foo, baz)"
    result = extractFunctionName(expression)
    assert result == "foo"


def test_extractFunctionName_name_with_special_characters():
    expression = "foo$bar(baz, qux)"
    result = extractFunctionName(expression)
    assert result == "foo$bar"


def test_extractFunctionName_name_nested_function():
    expression = "foo(bar(nested, function), baz)"
    result = extractFunctionName(expression)
    assert result == "foo"
