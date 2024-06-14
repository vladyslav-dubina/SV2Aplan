from enum import Enum, auto
from utils import generate_module_names, removeTrailingComma, Counters_Object
from structures.counters import CounterTypes
from typing import List


class ElementsTypes(Enum):
    ASSERT_ELEMENT = auto()
    IF_STATEMENT_ELEMENT = auto()
    ASSIGN_ELEMENT = auto()
    CONDITION_ELEMENT = auto()


class DeclTypes(Enum):
    WIRE = auto()
    INT = auto()
    REG = auto()
    INPORT = auto()
    OUTPORT = auto()
    IF_STATEMENT = auto()

    def checkType(type_str: str):
        if type_str == "int":
            return DeclTypes.INT
        return DeclTypes.INT


class B0:
    def __init__(self):
        self.elements = []


class ActionParts:
    def __init__(self):
        self.body: List[str] = []

    def __str__(self):
        body_to_str = ""
        for index, elem in enumerate(self.body):
            if index != 0:
                body_to_str += "; "
            body_to_str += elem
        return body_to_str


class Action:
    def __init__(self, name: str, number: int):
        self.name = name
        self.number = number
        self.name = self.name + "_" + str(number)
        self.precondition: ActionParts = ActionParts()
        self.postcondition: ActionParts = ActionParts()
        self.description: ActionParts = ActionParts()

    def getBody(self):
        return f""" = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""

    def getActionName(self):
        return "{0}_{1}".format(self.name, self.number)

    def __str__(self):
        return "{0}{1},".format(self.name, self.getBody())

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.getBody() == other.getBody()
        return False


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
        if self.data_type == DeclTypes.INT:
            return "int"
        elif (
            self.data_type == DeclTypes.INPORT
            or self.data_type == DeclTypes.OUTPORT
            or self.data_type == DeclTypes.WIRE
            or self.data_type == DeclTypes.REG
        ):
            if self.size == 0:
                return "bool"
            if self.size > 0:
                return "Bits " + str(self.size)


class Protocol:
    def __init__(self, identifier: str, sequence: int):
        self.identifier = identifier
        self.body: List[str] = []
        self.type: DeclTypes | None = None
        self.sequence = sequence

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
    def __init__(self, identifier: str, sequence: int):
        self.identifier = identifier
        self.sequence = sequence
        self.behavior: List[Protocol] = []

    def getLastBehaviorIndex(self):
        if not self.behavior:
            return None  # Повертаємо None, якщо список порожній
        return len(self.behavior) - 1

    def addProtocol(self, protocol_identifier: str):
        self.behavior.append(
            Protocol(
                protocol_identifier,
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
            )
        )
        return len(self.behavior) - 1

    def getBehInStrFormat(self):
        result = ""
        if len(self.behavior) > 0:
            result = "{0} = ".format(self.identifier)
            for index, element in enumerate(self.behavior):
                if index != 0:
                    result += ",\n"
                result += str(element)
        return result

    def getBehLen(self):
        return len(self.behavior)

    def __str__(self):
        result = ""
        for element in self.behavior:
            result += "\n"
            result += str(element)
        return result


class Always(Structure):
    def __init__(self, identifier: str, sensetive: str | None, sequence: int):
        super().__init__(identifier, sequence)
        self.sensetive = sensetive

    def getSensetiveForB0(self):
        result = ""
        if self.sensetive is not None:
            result = "Sensetive({0}, {1})".format(self.identifier, self.sensetive)
        else:
            result = "Sensetive({0})".format(self.identifier)
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

        self.out_of_block_elements: List[Protocol] = []

    def addDeclaration(self, decl: Declaration):
        self.declarations.append(decl)
        self.declarations = sorted(
            self.declarations,
            key=lambda elem: len(elem.identifier),
            reverse=True,
        )

    def getDeclarationsWithExpressions(self):
        result = []
        for element in self.declarations:
            if len(element.expression) > 0:
                result.append(element)
        return result

    def findDeclaration(self, identifier: str):
        for index, element in enumerate(self.declarations):
            if element.identifier == identifier:
                return index

    def updateDeclarationExpression(self, index: int, expression: str):
        self.declarations[index].expression = expression

    def isUniqAction(self, action: Action):

        for element in self.actions:
            if element == action:
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

    def isIncludeOutOfBlockElements(self):
        if len(self.out_of_block_elements) > 0:
            return True
        return False

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

    def getNoAlwaysStructures(self):
        result: List[Structure] = []
        for element in self.structures:
            if isinstance(element, Always) == False:
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

    def getOutOfBlockInStrFormat(self):
        result = ""
        for element in self.out_of_block_elements:
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

        protocols = self.out_of_block_elements + self.getNoAlwaysStructures()
        protocols.sort(key=lambda student: student.sequence)
        for index, element in enumerate(protocols):
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

        init_protocol = ""
        init_protocol_part = ""
        init_protocols_array = self.getDeclarationsWithExpressions()
        init_flag = False

        init_protocols_array.sort(key=lambda student: student.sequence)
        for index, element in enumerate(init_protocols_array):
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
