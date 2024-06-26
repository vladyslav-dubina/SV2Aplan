from enum import Enum, auto


class ElementsTypes(Enum):
    ASSERT_ELEMENT = auto()
    IF_STATEMENT_ELEMENT = auto()
    ASSIGN_ELEMENT = auto()
    ASSIGN_FOR_CALL_ELEMENT = auto()
    ASSIGN_OUT_OF_BLOCK_ELEMENT = auto()
    CONDITION_ELEMENT = auto()
    ACTION_ELEMENT = auto()
    GENERATE_ELEMENT = auto()
    PROTOCOL_ELEMENT = auto()
    MODULE_CALL_ELEMENT = auto()
    MODULE_ASSIGN_ELEMENT = auto()
    NONE_ELEMENT = auto()
