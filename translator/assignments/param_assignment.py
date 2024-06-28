from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module import Module
from classes.module_call import ModuleCall
from classes.parametrs import Parametr
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import is_numeric_string


def paramAssignment2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Param_assignmentContext,
    module_call: ModuleCall,
):
    identifier = ctx.parameter_identifier().getText()
    expression = ctx.constant_param_expression()
    expression_str = ""
    value = 0
    if expression is not None:
        numeric_string = is_numeric_string(expression.getText())
        if numeric_string is None:
            expression_str = expression.getText()
        else:
            value = numeric_string
    parametr_index = self.module.parametrs.addElement(
        Parametr(
            identifier,
            ctx.getSourceInterval(),
            value,
            expression_str,
        )
    )
    self.module.parametrs.evaluateParametrExpressionByIndex(parametr_index)
    if module_call is not None:
        source_parametr = module_call.paramets.findElement(identifier)
        if source_parametr is not None:
            parametr = self.module.parametrs.getElementByIndex(parametr_index)
            parametr.value = source_parametr.value
