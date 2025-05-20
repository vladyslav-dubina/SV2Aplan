from enum import Enum, auto


class ElementsTypes(Enum):
    ASSERT_ELEMENT = auto()
    IF_STATEMENT_ELEMENT = auto()
    CASE_STATEMENT_ELEMENT = auto()
    CASE_ELEMENT = auto()
    ELSE_BODY_ELEMENT = auto()
    ASSIGN_ELEMENT = auto()
    ASSIGN_SENSETIVE_ELEMENT = auto()
    ASSIGN_FOR_CALL_ELEMENT = auto()
    ASSIGN_ARRAY_FOR_CALL_ELEMENT = auto()
    ASSIGN_OUT_OF_BLOCK_ELEMENT = auto()
    CONDITION_ELEMENT = auto()
    ACTION_ELEMENT = auto()
    GENERATE_STATEMENT_ELEMENT = auto()
    GENERATE_ELEMENT = auto()
    PROTOCOL_ELEMENT = auto()
    MODULE_CALL_ELEMENT = auto()
    MODULE_ASSIGN_ELEMENT = auto()
    ALWAYS_ELEMENT = auto()
    INITIAL_ELEMENT = auto()
    REPEAT_ELEMENT = auto()
    TASK_ELEMENT = auto()
    FUNCTION_ELEMENT = auto()
    ARRAY_ELEMENT = auto()
    ARRAY_SIZE_ELEMENT = auto()

    # LOOPS
    LOOP_ELEMENT = auto()
    FOREVER_ELEMENT = auto()
    WHILE_ELEMENT = auto()

    # Agents types
    MODULE_ELEMENT = auto()
    PACKAGE_ELEMENT = auto()
    CLASS_ELEMENT = auto()
    OBJECT_ELEMENT = auto()
    INTERFACE_ELEMENT = auto()

    # Node
    NUMBER_ELEMENT = auto()
    IDENTIFIER_ELEMENT = auto()
    OPERATOR_ELEMENT = auto()
    DOT_ELEMENT = auto()
    SEMICOLON_ELEMENT = auto()
    NONE_ELEMENT = auto()

    PRECONDITION_ELEMENT = auto()
    POSTCONDITION_ELEMENT = auto()

    IF_PREDICATE = auto()
    IF_ELSE_PREDICATE = auto()
    ELSE_PREDICATE = auto()
    IF_CONDITION_LEFT = auto()
    IF_CONDITION_RIGTH = auto()
