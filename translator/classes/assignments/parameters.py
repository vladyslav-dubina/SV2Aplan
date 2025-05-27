from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.value_parametrs import ValueParametr
from translator.classes.base_translator import BaseTranslator
from utils.utils import isNumericString


class ParametrsAssignmentTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Param_assignmentContext
            | SystemVerilogParser.Local_parameter_declarationContext
        ),
    ) -> None:

        if isinstance(ctx, SystemVerilogParser.Local_parameter_declarationContext):
            declaration = ctx.list_of_param_assignments().param_assignment()
            for elem in declaration:
                identifier = elem.parameter_identifier().identifier().getText()
                expression = elem.constant_param_expression()
                if expression is not None:
                    expression = expression.getText()
                else:
                    expression = "0"

                self.createParametr(
                    self, identifier, expression, elem.getSourceInterval()
                )

        elif isinstance(ctx, SystemVerilogParser.Param_assignmentContext):
            identifier = ctx.parameter_identifier().getText()
            expression = ctx.constant_param_expression()
            if expression is not None:
                expression = expression.getText()
            else:
                expression = "0"

            self.createParametr(identifier, expression, ctx.getSourceInterval())

    def createParametr(
        self,
        identifier: str,
        expression: str,
        source_interval: Tuple[int, int],
    ):
        expression_str = ""
        value = 0
        if expression is not None:
            numeric_string = isNumericString(expression)
            if numeric_string is None:
                expression_str = expression
            else:
                value = numeric_string
        parametr_index = self.module.value_parametrs.addElement(
            ValueParametr(
                identifier,
                source_interval,
                value,
                expression_str,
            )
        )
        self.module.value_parametrs.evaluateParametrExpressionByIndex(parametr_index)
        if self.module_call is not None:
            source_parametr = self.module_call.paramets.findElement(identifier)
            if source_parametr is not None:
                parametr = self.module.value_parametrs.getElementByIndex(parametr_index)
                parametr.value = source_parametr.value
