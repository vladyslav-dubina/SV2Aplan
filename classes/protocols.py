import re
from typing import Tuple, List
from classes.parametrs import ParametrArray
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma
from classes.element_types import ElementsTypes
from utils.utils import extractFunctionName


class BodyElement(Basic):
    def __init__(
        self,
        identifier: str,
        pointer_to_related: Basic | None = None,
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        parametrs: ParametrArray = ParametrArray(),
    ):

        super().__init__(identifier, (0, 0), element_type)
        self.parametrs = parametrs
        self.pointer_to_related = pointer_to_related

    def getName(self):
        if self.parametrs:
            if self.parametrs.getLen() == 0:
                return self.identifier
            else:
                return "{0}({1})".format(self.identifier, str(self.parametrs))
        else:
            return self.identifier


class Protocol(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        parametrs: ParametrArray | None = None,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.body: List[BodyElement] = []
        self.parametrs: ParametrArray = ParametrArray()
        if parametrs is not None:
            self.parametrs = parametrs

    def copy(self):
        protocol = Protocol(self.identifier, self.source_interval, self.element_type)
        for element in self.body:
            protocol.body.append(element)
        protocol.parametrs = self.parametrs.copy()
        protocol.number = self.number
        return protocol

    def addBody(self, body: BodyElement):
        self.body.append(body)

    def getName(self):
        identifier = self.identifier
        if self.number:
            identifier = "{0}_{1}".format(identifier, self.number)
        if self.parametrs.getLen() > 0:
            identifier = "{0}({1})".format(identifier, str(self.parametrs))

        return identifier

    def updateLinks(self, module):
        for index, element in enumerate(self.body):
            func_name = extractFunctionName(element.identifier)
            if func_name:
                action = module.actions.findElement(func_name)
                if action:
                    self.body[index] = (
                        action,
                        element.element_type,
                        element.element_type,
                    )

    def __str__(self):
        body_to_str = ""
        for index, body_element in enumerate(self.body):
            element_str = body_element.getName()
            protocol_element = False
            if index != 0:
                if self.element_type == ElementsTypes.GENERATE_ELEMENT:
                    body_to_str += " || "
                else:
                    prev_body_element = self.body[index - 1]
                    if body_element.element_type == ElementsTypes.FOREVER_ELEMENT:
                        body_to_str += ";"
                    elif (
                        body_element.element_type == ElementsTypes.IF_CONDITION_RIGTH
                        and prev_body_element.element_type
                        == ElementsTypes.IF_CONDITION_LEFT
                    ):
                        body_to_str += " + "
                    elif (
                        prev_body_element.element_type == ElementsTypes.ACTION_ELEMENT
                        and (
                            body_element.element_type == ElementsTypes.ACTION_ELEMENT
                            or body_element.element_type
                            == ElementsTypes.PROTOCOL_ELEMENT
                        )
                    ):
                        body_to_str += "."
                    else:
                        protocol_element = True
                        body_to_str += ";"

            if body_element.pointer_to_related is not None:
                element_str = re.sub(
                    r"\b{}\b".format(
                        re.escape(body_element.pointer_to_related.identifier)
                    ),
                    body_element.pointer_to_related.getName(),
                    element_str,
                )

            if body_element.element_type == ElementsTypes.FOREVER_ELEMENT:
                body_to_str += "{" + element_str + "}"
            elif protocol_element == False:
                body_to_str += element_str
            else:
                body_to_str += "(" + element_str + ")"
            if index == len(self.body) - 1:
                body_to_str += ","

        return "{0} = {1}".format(
            self.getName(),
            body_to_str,
        )

    def __repr__(self):
        return f"\tProtocol({self.identifier!r}, {self.sequence!r})\n"


class ProtocolArray(BasicArray):
    def __init__(self):
        super().__init__(Protocol)

    def copy(self):
        new_aray: ProtocolArray = ProtocolArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: ProtocolArray = ProtocolArray()
        elements = self.elements

        if include is None and exclude is None:
            return self

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                include_identifier is not None
                and element.identifier is not include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier is exclude_identifier
            ):
                continue

            result.addElement(element)

        return result

    def updateLinks(self, module):
        for element in self.getElements():
            element.updateLinks(module)

    def getProtocolsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def __repr__(self):
        return f"ProtocolsArray(\n{self.elements!r}\n)"
