from enum import Enum, auto

from classes.element_types import ElementsTypes


class CounterTypes(Enum):
    ASSIGNMENT_COUNTER = auto()
    IF_COUNTER = auto()
    ALWAYS_COUNTER = auto()
    B_COUNTER = auto()
    ASSERT_COUNTER = auto()
    MODULE_COUNTER = auto()
    BODY_COUNTER = auto()
    ELSE_BODY_COUNTER = auto()
    LOOP_COUNTER = auto()
    CONDITION_COUNTER = auto()
    NONE_COUNTER = auto()
    SEQUENCE_COUNTER = auto()
    UNIQ_NAMES_COUNTER = auto()


class Counters:
    def __init__(self) -> None:
        self.module_counter = 1
        self.assignment_counter = 1
        self.if_counter = 0
        self.always_counter = 0
        self.assert_counter = 1
        self.b_counter = 0
        self.body_counter = 1
        self.else_body_counter = 1
        self.loop_counter = 1
        self.cond_counter = 1
        self.sequence = 0
        self.uniq_names_counter = 1

    def selectCounter(self, element_type: ElementsTypes):
        if element_type is ElementsTypes.ASSIGN_ELEMENT:
            return CounterTypes.ASSIGNMENT_COUNTER
        if element_type is ElementsTypes.IF_STATEMENT_ELEMENT:
            return CounterTypes.IF_COUNTER
        if element_type is ElementsTypes.ALWAYS_ELEMENT:
            return CounterTypes.ALWAYS_COUNTER
        if element_type is ElementsTypes.ASSERT_ELEMENT:
            return CounterTypes.ASSERT_COUNTER
        if element_type is ElementsTypes.ELSE_BODY_ELEMENT:
            return CounterTypes.ELSE_BODY_COUNTER
        if element_type is ElementsTypes.LOOP_ELEMENT:
            return CounterTypes.LOOP_COUNTER
        return CounterTypes.NONE_COUNTER

    def incrieseCounter(self, counter_type: CounterTypes):
        if counter_type is CounterTypes.ASSIGNMENT_COUNTER:
            self.assignment_counter += 1
        if counter_type is CounterTypes.IF_COUNTER:
            self.if_counter += 1
        if counter_type is CounterTypes.ALWAYS_COUNTER:
            self.always_counter += 1
        if counter_type is CounterTypes.ASSERT_COUNTER:
            self.assert_counter += 1
        if counter_type is CounterTypes.B_COUNTER:
            self.b_counter += 1
        if counter_type is CounterTypes.MODULE_COUNTER:
            self.module_counter += 1
        if counter_type is CounterTypes.BODY_COUNTER:
            self.body_counter += 1
        if counter_type is CounterTypes.ELSE_BODY_COUNTER:
            self.else_body_counter += 1
        if counter_type is CounterTypes.LOOP_COUNTER:
            self.loop_counter += 1
        if counter_type is CounterTypes.CONDITION_COUNTER:
            self.cond_counter += 1
        if counter_type is CounterTypes.SEQUENCE_COUNTER:
            self.sequence += 1
        if counter_type is CounterTypes.UNIQ_NAMES_COUNTER:
            self.uniq_names_counter += 1

    def decrieseCounter(self, counter_type: CounterTypes):
        if counter_type is CounterTypes.ASSIGNMENT_COUNTER:
            self.assignment_counter -= 1
        if counter_type is CounterTypes.IF_COUNTER:
            self.if_counter -= 1
        if counter_type is CounterTypes.ALWAYS_COUNTER:
            self.always_counter -= 1
        if counter_type is CounterTypes.ASSERT_COUNTER:
            self.assert_counter -= 1
        if counter_type is CounterTypes.B_COUNTER:
            self.b_counter -= 1
        if counter_type is CounterTypes.MODULE_COUNTER:
            self.module_counter -= 1
        if counter_type is CounterTypes.BODY_COUNTER:
            self.body_counter -= 1
        if counter_type is CounterTypes.ELSE_BODY_COUNTER:
            self.else_body_counter -= 1
        if counter_type is CounterTypes.LOOP_COUNTER:
            self.loop_counter -= 1
        if counter_type is CounterTypes.CONDITION_COUNTER:
            self.cond_counter -= 1
        if counter_type is CounterTypes.SEQUENCE_COUNTER:
            self.sequence -= 1
        if counter_type is CounterTypes.UNIQ_NAMES_COUNTER:
            self.uniq_names_counter -= 1

    def getCounter(self, counter_type: CounterTypes):
        if counter_type is CounterTypes.ASSIGNMENT_COUNTER:
            return self.assignment_counter
        if counter_type is CounterTypes.IF_COUNTER:
            return self.if_counter
        if counter_type is CounterTypes.ALWAYS_COUNTER:
            return self.always_counter
        if counter_type is CounterTypes.ASSERT_COUNTER:
            return self.assert_counter
        if counter_type is CounterTypes.B_COUNTER:
            return self.b_counter
        if counter_type is CounterTypes.MODULE_COUNTER:
            return self.module_counter
        if counter_type is CounterTypes.BODY_COUNTER:
            return self.body_counter
        if counter_type is CounterTypes.ELSE_BODY_COUNTER:
            return self.else_body_counter
        if counter_type is CounterTypes.LOOP_COUNTER:
            return self.loop_counter
        if counter_type is CounterTypes.CONDITION_COUNTER:
            return self.cond_counter
        if counter_type is CounterTypes.SEQUENCE_COUNTER:
            self.incrieseCounter(CounterTypes.SEQUENCE_COUNTER)
            return self.sequence
        if counter_type is CounterTypes.UNIQ_NAMES_COUNTER:
            return self.uniq_names_counter

    def countersDeinit(self):
        self.module_counter = 1
        self.assignment_counter = 1
        self.if_counter = 0
        self.always_counter = 0
        self.assert_counter = 1
        self.b_counter = 0
        self.body_counter = 1
        self.else_body_counter = 1
        self.loop_counter = 1
        self.cond_counter = 1
        self.sequence = 0
        self.uniq_names_counter = 1
