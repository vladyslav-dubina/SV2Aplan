from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module import Module
from classes.module_call import ModuleCall
from classes.value_parametrs import ValueParametr
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import isNumericString


def createParametr(
    self: SV2aplan,
    identifier: str,
    expression: str,
    source_interval: Tuple[int, int],
    module_call: ModuleCall,
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
    if module_call is not None:
        source_parametr = module_call.paramets.findElement(identifier)
        if source_parametr is not None:
            parametr = self.module.value_parametrs.getElementByIndex(parametr_index)
            parametr.value = source_parametr.value


def paramAssignment2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Param_assignmentContext
        | SystemVerilogParser.Local_parameter_declarationContext
    ),
    module_call: ModuleCall,
):
    if isinstance(ctx, SystemVerilogParser.Local_parameter_declarationContext):
        declaration = ctx.list_of_param_assignments().param_assignment()
        for elem in declaration:
            identifier = elem.parameter_identifier().identifier().getText()
            expression = elem.constant_param_expression()
            if expression is not None:
                expression = expression.getText()
            else:
                expression = "0"

            createParametr(
                self, identifier, expression, elem.getSourceInterval(), module_call
            )

    elif isinstance(ctx, SystemVerilogParser.Param_assignmentContext):
        identifier = ctx.parameter_identifier().getText()
        expression = ctx.constant_param_expression()
        if expression is not None:
            expression = expression.getText()
        else:
            expression = "0"

        createParametr(
            self, identifier, expression, ctx.getSourceInterval(), module_call
        )
