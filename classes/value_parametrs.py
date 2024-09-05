from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes


class ValueParametr(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        value: int = 0,
        expression: str | None = None,
    ):
        super().__init__(identifier, source_interval)
        self.value = value
        self.expression = expression

    def copy(self):
        parametr = ValueParametr(
            self.identifier, self.source_interval, self.value, self.expression
        )
        parametr.number = self.number
        return parametr

    def prepareExpression(self):
        from utils.string_formating import (
            valuesToAplanStandart,
            doubleOperators2Aplan,
            addSpacesAroundOperators,
            addBracketsAfterTilda,
            addBracketsAfterNegation,
            addLeftValueForUnaryOrOperator,
            vectorSizes2AplanStandart,
            generatePythonStyleTernary,
            replace_cpp_operators,
        )

        expression = valuesToAplanStandart(self.expression)
        expression = doubleOperators2Aplan(expression)
        expression = addLeftValueForUnaryOrOperator(expression)
        expression = addSpacesAroundOperators(expression)
        expression = addBracketsAfterNegation(expression)
        expression = addBracketsAfterTilda(expression)
        expression = vectorSizes2AplanStandart(expression)
        expression = replace_cpp_operators(expression)
        expression = generatePythonStyleTernary(expression)
        self.expression = expression

    def __repr__(self):
        return f"\tParametr({self.identifier!r}, {self.value!r}, {self.expression!r})\n"


class ValueParametrArray(BasicArray):
    def __init__(self):
        super().__init__(ValueParametr)

    def copy(self):
        new_aray: ValueParametrArray = ValueParametrArray()
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
        result: ValueParametrArray = ValueParametrArray()
        elements = self.elements

        if include is None and exclude is None:
            return self.copy()

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

    def addElement(self, new_element: ValueParametr):
        if isinstance(new_element, self.element_type):
            new_element.prepareExpression()
            self.elements.append(new_element)
            self.elements = sorted(
                self.elements,
                key=lambda element: len(element.identifier),
                reverse=True,
            )
            return self.getElementIndex(new_element.identifier)
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def evaluateParametrExpressionByIndex(self, index: int):
        from utils.string_formating import replaceValueParametrsCalls
        from utils.utils import evaluateExpression

        parametr = self.getElementByIndex(index)
        expression = parametr.expression
        if len(expression) > 0:
            expression = replaceValueParametrsCalls(self, expression)
            expression = evaluateExpression(expression)
            parametr.value = expression
        return expression

    def __repr__(self):
        return f"ParametrsArray(\n{self.elements!r}\n)"
