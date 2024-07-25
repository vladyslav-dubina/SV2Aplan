from typing import Tuple
from classes.basic import Basic, BasicArray


class Parametr(Basic):
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
        parametr = Parametr(
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


class ParametrArray(BasicArray):
    def __init__(self):
        super().__init__(Parametr)

    def copy(self):
        new_aray: ParametrArray = ParametrArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def addElement(self, new_element: Parametr):
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
        from utils.string_formating import replaceParametrsCalls
        from utils.utils import evaluateExpression

        parametr = self.getElementByIndex(index)
        expression = parametr.expression
        if len(expression) > 0:
            expression = replaceParametrsCalls(self, expression)
            expression = evaluateExpression(expression)
            parametr.value = expression
        return expression

    def recalculateParametrValue(self):
        for index, element in enumerate(self.getElements()):
            self.evaluateParametrExpressionByIndex(index)

    def __repr__(self):
        return f"ParametrsArray(\n{self.elements!r}\n)"
