from enum import Enum, auto
from utils import generate_module_names, removeTrailingComma, increaseSequence
from typing import List, Optional


class DeclTypes(Enum):
    WIRE = auto()
    REG = auto()
    INPORT = auto()
    OUTPORT = auto()


class CounterTypes(Enum):
    ASSIGNMENT_COUNTER = auto()
    IF_COUNTER = auto()
    ALWAYS_COUNTER = auto()
    B_COUNTER = auto()
    ASSERT = auto()


class B0:
    def __init__(self):
        self.elements = []


class Action:
    def __init__(self, name: str, number: int, body: str):
        self.name = name
        self.number = number
        self.name = self.name + str(number)
        self.body = body

    def getActionName(self):
        return "{0}_{1}".format(self.name, self.number)

    def __str__(self):
        return "{0},".format(self.body)


class Declaration:
    def __init__(
        self,
        data_type: DeclTypes,
        identifier: str,
        expression: str,
        size: int,
        sequence: int,
    ):
        self.data_type = data_type
        self.identifier = identifier
        self.expression = expression
        self.size = size
        self.sequence = sequence

    def getAplanDecltype(self):
        if self.data_type == DeclTypes.WIRE:
            return "bool"
        if self.data_type == DeclTypes.REG:
            return "bool"
        if self.data_type == DeclTypes.INPORT or self.data_type == DeclTypes.OUTPORT:
            if self.size == 0:
                return "bool"
            if self.size > 0:
                return "Bits " + str(self.size)


class Protocol:
    def __init__(self, identifier: str, sequence: int):
        self.sequence = sequence
        self.identifier = identifier
        self.body: List[str] = []

    def identifierToBody(self):
        self.body.insert(0, self.identifier)
        self.identifier = ""

    def setIdentifier(self, identifier: str):
        self.identifier = identifier

    def setBody(self, body: str):
        self.body.clear()
        self.body.append(body)

    def addBody(self, body: str):
        self.body.append(body)

    def __str__(self):
        body_to_str = ""
        for index, elem in enumerate(self.body):
            if index != 0:
                body_to_str += "."
            body_to_str += elem
            if index == len(self.body) - 1:
                body_to_str += ","
        return "{0} = {1}".format(self.identifier, body_to_str)


class Structure:
    def __init__(self, identifier: str, sequence: int):
        self.sequence = sequence
        self.identifier = identifier
        self.behavior: List[Protocol] = []

    def getLastBehaviorIndex(self):
        if not self.behavior:
            return None  # Повертаємо None, якщо список порожній
        return len(self.behavior) - 1

    def addProtocol(self, protocol_identifier: str):
        self.behavior.append(Protocol(protocol_identifier, self.sequence))
        return len(self.behavior) - 1

    def getBehInStrFormat(self):
        pass

    def getBehLen(self):
        return len(self.behavior)

    def __str__(self):
        return ""


class Always(Structure):
    def __init__(self, identifier: str, sensetive: str | None, sequence: int):
        super().__init__(identifier, sequence)
        self.sensetive = sensetive

    def getBehInStrFormat(self):
        result = ""
        if len(self.behavior) > 0:
            result = "{0} = ".format(self.identifier)
            for index, element in enumerate(self.behavior):
                if index != 0:
                    result += ",\n"
                result += str(element)
        return result

    def getSensetiveForB0(self):
        result = ""
        if self.sensetive is not None:
            result = "Sensetive({0}, {1})".format(self.identifier, self.sensetive)
        else:
            result = "Sensetive({0})".format(self.identifier)
        return result

    def __str__(self) -> str:
        result = ""
        for element in self.behavior:
            result += "\n"
            result += str(element)
        return result


class Module:
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.ident_uniq_name = generate_module_names()
        self.identifierUpper = self.identifier.upper()

        # arrays
        self.declarations: List[Declaration] = []
        self.actions: List[Action] = []

        self.structures: List[Structure] = []

        self.notBlockElements: List[Protocol] = []

        # counters
        self.assignment_counter = 0
        self.if_counter = 0
        self.always_counter = 0
        self.assert_counter = 0
        self.b_counter = 0

    def isIncludeInputPorts(self):
        for element in self.declarations:
            if element.data_type == DeclTypes.INPORT:
                return True
        return False

    def getInputPorts(self):
        result: List[Declaration] = []
        for element in self.declarations:
            if element.data_type == DeclTypes.INPORT:
                result.append(element)
        return result

    def isIncludeOutputPorts(self):
        for element in self.declarations:
            if element.data_type == DeclTypes.OUTPORT:
                return True
        return False

    def getOutputPorts(self):
        result: List[Declaration] = []
        for element in self.declarations:
            if element.data_type == DeclTypes.OUTPORT:
                result.append(element)
        return result

    def isIncludeNonBlockElements(self):
        if len(self.notBlockElements) > 0:
            return True
        return False

    def isIncludeWires(self):
        for element in self.declarations:
            if element.data_type == DeclTypes.WIRE:
                return True
        return False

    def getWires(self, assignment: bool):
        result: List[Declaration] = []
        for element in self.declarations:
            if element.data_type == DeclTypes.WIRE:
                if assignment:
                    if len(element.expression) > 0:
                        result.append(element)
                else:
                    result.append(element)
        return result

    def isIncludeRegs(self):
        for element in self.declarations:
            if element.data_type == DeclTypes.REG:
                return True
        return False

    def getRegs(self, assignment: bool):
        result: List[Declaration] = []
        for element in self.declarations:
            if element.data_type == DeclTypes.REG:
                if assignment:
                    if len(element.expression) > 0:
                        result.append(element)
                else:
                    result.append(element)
        return result

    def isIncludeAlways(self):
        for element in self.structures:
            if isinstance(element, Always):
                return True
        return False

    def getAlwaysList(self):
        result: List[Always] = []
        for element in self.structures:
            if isinstance(element, Always):
                result.append(element)
        return result

    def incrieseCounter(self, counter_type: CounterTypes):
        if counter_type is CounterTypes.ASSIGNMENT_COUNTER:
            self.assignment_counter += 1
        if counter_type is CounterTypes.IF_COUNTER:
            self.if_counter += 1
        if counter_type is CounterTypes.ALWAYS_COUNTER:
            self.always_counter += 1
        if counter_type is CounterTypes.B_COUNTER:
            self.b_counter += 1
        if counter_type is CounterTypes.ASSERT:
            self.assert_counter += 1

    def getActionsInStrFormat(self):
        result = ""
        for element in self.actions:
            result += "\n"
            result += str(element)

        result = removeTrailingComma(result)

        return result

    def getStructuresInStrFormat(self):
        result = ""
        for element in self.structures:
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def getNotBlockElementsInStrFormat(self):
        result = ""
        for element in self.notBlockElements:
            result += "\n"
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def getBehInitProtocols(self):
        result = ""

        wires = self.getWires(True)
        regs = self.getRegs(True)
        always_list = self.getAlwaysList()
        combined_array = wires + regs + always_list + self.notBlockElements
        combined_array.sort(key=lambda obj: obj.sequence)

        for index, element in enumerate(combined_array):
            if type(element) is Declaration:
                if len(element.expression) > 0:
                    if index != 0:
                        result += "."
                    result += element.expression
            elif type(element) is Always:
                if index != 0:
                    result += "."
                result += element.getSensetiveForB0()
            elif type(element) is Protocol:
                if index != 0:
                    result += "."
                result += element.identifier

        return result
