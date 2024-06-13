from enum import Enum, auto
from utils import generate_module_names, removeTrailingComma
from typing import List, Optional
import difflib


class DeclTypes(Enum):
    WIRE = auto()
    REG = auto()
    INPORT = auto()
    OUTPORT = auto()
    IF_STATEMENT = auto()


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
        return "{0}{1},".format(self.name, self.body)


class Declaration:
    def __init__(
        self,
        data_type: DeclTypes,
        identifier: str,
        expression: str,
        size: int,
    ):
        self.data_type = data_type
        self.identifier = identifier
        self.expression = expression
        self.size = size

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
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.body: List[str] = []
        self.type: DeclTypes | None = None

    def setType(self, type: DeclTypes | None):
        self.type = type

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
    def __init__(self, identifier: str):
        self.identifier = identifier
        self.behavior: List[Protocol] = []

    def getLastBehaviorIndex(self):
        if not self.behavior:
            return None  # Повертаємо None, якщо список порожній
        return len(self.behavior) - 1

    def addProtocol(self, protocol_identifier: str):
        self.behavior.append(Protocol(protocol_identifier))
        return len(self.behavior) - 1

    def getBehInStrFormat(self):
        pass

    def getBehLen(self):
        return len(self.behavior)

    def __str__(self):
        return ""


class Always(Structure):
    def __init__(self, identifier: str, sensetive: str | None):
        super().__init__(identifier)
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

        self.not_block_elements: List[Protocol] = []

    def isUniqAction(self, action_body: str):

        for element in self.actions:
            if element.body == action_body:
                print(element.name)
                return element.name
        return None

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
        if len(self.not_block_elements) > 0:
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

    def getnot_block_elementsInStrFormat(self):
        result = ""
        for element in self.not_block_elements:
            result += "\n"
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def getBehInitProtocols(self):
        result = ""

        # MAIN PROTOCOL
        main_protocol = ""
        main_protocol_part = ""
        main_flag = False

        for index, element in enumerate(self.not_block_elements):
            if index != 0:
                main_protocol += "."
            main_protocol += element.identifier

        if len(main_protocol) > 0:
            main_flag = True
            main_protocol = "MAIN = " + main_protocol + ","
            main_protocol_part = "MAIN"
            result += main_protocol

        # ALWAYS PART
        always_list = self.getAlwaysList()
        always_part = ""
        always_flag = False

        for index, element in enumerate(always_list):
            if index != 0:
                always_part += " || "
            always_part += element.getSensetiveForB0()

        if len(always_part) > 0:
            always_flag = True
            if len(always_list) > 1:
                always_part = "{" + always_part + "}"
            if main_flag:
                always_part += ";"

        # INIT PROTOCOL
        wires = self.getWires(True)
        regs = self.getRegs(True)

        init_protocol = ""
        init_protocol_part = ""
        init_protocols_array = wires + regs
        init_flag = False

        for index, element in enumerate(init_protocols_array):
            if len(element.expression) > 0:
                if index != 0:
                    init_protocol += "."
                init_protocol += element.expression

        if len(init_protocol) > 0:
            init_flag = True
            init_protocol = "INIT = " + init_protocol + ",\n"
            init_protocol_part = "INIT"
            if main_flag or always_flag:
                init_protocol_part += ";"
            result = init_protocol + result

        b0 = f"B = ({init_protocol_part}{always_part}{main_protocol_part}),"
        if main_flag or init_flag:
            b0 += "\n"
        result = b0 + result
        return result
