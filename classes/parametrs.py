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

    def prepareExpression(self):
        from utils import (
            valuesToAplanStandart,
            doubleOperators2Aplan,
            addSpacesAroundOperators,
            addBracketsAfterTilda,
            vectorSizes2AplanStandart,
            generatePythonStyleTernary,
            replace_cpp_operators,
        )

        expression = valuesToAplanStandart(self.expression)
        expression = doubleOperators2Aplan(expression)
        expression = addSpacesAroundOperators(expression)
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
        from utils import replaceParametrsCalls, evaluateExpression

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
