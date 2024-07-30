import pytest
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.utils import (
    evaluateExpression,
    extractDimentionSize,
    extractFunctionName,
    extractParameters,
    extractVectorSize,
    format_time,
    getValuesLeftOfEqualsOrDot,
    isFunctionCallPresentAndReplace,
    isNumericString,
    isVariablePresent,
    vectorSize2AplanVectorSize,
    removeTypeFromForInit,
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


# =========================== REMOVE_TYPE_FROMFOR_INIT ================================


def test_removeTypeFromForInit_single_variable():
    mock_ctx = MagicMock()

    mock_var_decl = MagicMock()
    mock_var_decl.variable_identifier.return_value.getText.return_value = "var1"
    mock_var_decl.expression.return_value.getText.return_value = "value1"

    mock_ctx.for_variable_declaration.return_value = [mock_var_decl]

    result = removeTypeFromForInit(mock_ctx)
    assert result == "var1=value1"


def test_removeTypeFromForInit_multiple_variables():
    mock_ctx = MagicMock()

    mock_var_decl1 = MagicMock()
    mock_var_decl1.variable_identifier.return_value.getText.return_value = "var1"
    mock_var_decl1.expression.return_value.getText.return_value = "value1"

    mock_var_decl2 = MagicMock()
    mock_var_decl2.variable_identifier.return_value.getText.return_value = "var2"
    mock_var_decl2.expression.return_value.getText.return_value = "value2"

    mock_ctx.for_variable_declaration.return_value = [mock_var_decl1, mock_var_decl2]

    result = removeTypeFromForInit(mock_ctx)
    assert result == "var1=value1var2=value2"


def test_removeTypeFromForInit_empty():
    mock_ctx = MagicMock()
    mock_ctx.for_variable_declaration.return_value = []

    result = removeTypeFromForInit(mock_ctx)
    assert result == ""


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


# ============================ IS_FUNCTION_CALL_PRESENT_AND_REPLACE ==================================


def test_isFunctionCallPresentAndReplace_basic():
    expression = "foo(bar)"
    variable = "foo"
    replacement = "baz"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "baz"
    assert function_call == "foo(bar)"


def test_isFunctionCallPresentAndReplace_with_arguments():
    expression = "foo(bar, baz)"
    variable = "foo"
    replacement = "newFunc"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "newFunc"
    assert function_call == "foo(bar, baz)"


def test_isFunctionCallPresentAndReplace_with_namespace():
    expression = "namespace.foo(bar)"
    variable = "foo"
    replacement = "updatedFunc"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "updatedFunc"
    assert function_call == "namespace.foo(bar)"


def test_isFunctionCallPresentAndReplace_with_no_match():
    expression = "foo(bar)"
    variable = "baz"
    replacement = "replacement"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is False
    assert modified_expression == "foo(bar)"
    assert function_call == ""


def test_isFunctionCallPresentAndReplace_with_partial_match():
    expression = "foo(bar) and fooAnother()"
    variable = "foo"
    replacement = "newFunction"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "newFunction and fooAnother()"
    assert function_call == "foo(bar)"


def test_isFunctionCallPresentAndReplace_with_edge_cases():
    # Function call with special characters
    expression = "foo_$bar()"
    variable = "foo_$bar"
    replacement = "replacementFunc"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "replacementFunc"
    assert function_call == "foo_$bar()"

    # Empty expression
    expression = ""
    variable = "foo"
    replacement = "replacement"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is False
    assert modified_expression == ""
    assert function_call == ""

    # Variable with special characters
    expression = "foo(1) bar()"
    variable = "foo"
    replacement = "updatedFoo"

    is_present, modified_expression, function_call = isFunctionCallPresentAndReplace(
        expression, variable, replacement
    )

    assert is_present is True
    assert modified_expression == "updatedFoo bar()"
    assert function_call == "foo(1)"


# ============================ EXTRACT_PARAMETERS ==================================
def test_extractParameters_basic():
    expression = "foo(bar, baz)"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["bar", "baz"]


def test_extractParameters_with_spaces():
    expression = "foo(  bar  ,  baz  )"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["bar", "baz"]


def test_extractParameters_empty():
    expression = "foo()"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == []


def test_extractParameters_with_single_parameter():
    expression = "foo(bar)"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["bar"]


def test_extractParameters_with_trailing_comma():
    expression = "foo(bar, baz,)"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["bar", "baz"]


def test_extractParameters_with_no_match():
    expression = "foo(bar, baz)"
    function_name = "bar"

    result = extractParameters(expression, function_name)

    assert result == []


def test_extractParameters_with_nested_parentheses():
    expression = "foo(bar, nestedFunc(a, b), baz)"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["bar", "nestedFunc(a, b)", "baz"]


def test_extractParameters_with_special_characters():
    expression = "foo(a_$var, some_var!)"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == ["a_$var", "some_var!"]


def test_extractParameters_empty_function_name():
    expression = "foo(bar, baz)"
    function_name = ""

    result = extractParameters(expression, function_name)

    assert result == []


def test_extractParameters_no_parentheses():
    expression = "foo bar, baz"
    function_name = "foo"

    result = extractParameters(expression, function_name)

    assert result == []


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


# ============================ GET_VALUES_LEFT_OF_EQUALS_OR_DOT ==================================


def test_getValuesLeftOfEqualsOrDot():
    expression = "x = 5; y = 10; z = 15"
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == ["x", "y", "z"]


def test_get_values_left_of_dot():
    expression = "object.property = value; anotherObject.method()"
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == ["property", "object", "anotherObject"]


def test_getValuesLeftOfEqualsOrDot_and_dot():
    expression = "x = 5; object.property = value; y = 10; anotherObject.method()"
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == ["x", "property", "y", "object", "anotherObject"]


def test_no_equals_or_dot():
    expression = "this is a test string without equals or dot"
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == []


def test_empty_string():
    expression = ""
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == []


def test_values_with_spaces():
    expression = "  x  =  5;  y  =  10;  z  =  15  "
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == ["x", "y", "z"]


def test_mixed_cases():
    expression = "X = 5; y = 10; Object.property = value; AnotherObject.method()"
    result = getValuesLeftOfEqualsOrDot(expression)
    assert result == ["X", "y", "property", "Object", "AnotherObject"]
