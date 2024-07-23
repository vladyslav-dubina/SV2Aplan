import re
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module import Module
from classes.processed import ProcessedElement
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import (
    parallelAssignment2Assignment,
    replace_cpp_operators,
    replaceParametrsCalls,
)
from utils.utils import Counters_Object


def replaceGenvarToValue(expression: str, genvar: str, value: int):
    expression = re.sub(
        r"\b{}\b".format(re.escape(genvar)),
        f"{value}",
        expression,
    )
    return expression


def generateBodyToAplan(
    self: SV2aplan, ctx, sv_structure: Structure, init_var_name, current_value
):
    if ctx.getChildCount() == 0:
        return
    for child in ctx.getChildren():
        if (
            type(child) is SystemVerilogParser.Variable_decl_assignmentContext
            or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
            or type(child) is SystemVerilogParser.Net_assignmentContext
            or type(child) is SystemVerilogParser.Variable_assignmentContext
        ):
            expression = child.getText()
            expression = replaceGenvarToValue(expression, init_var_name, current_value)
            self.module.processed_elements.addElement(
                ProcessedElement("action", child.getSourceInterval())
            )
            (
                action_pointer,
                action_name,
                source_interval,
                uniq_action,
            ) = self.expression2Aplan(
                expression,
                ElementsTypes.ASSIGN_ELEMENT,
                child.getSourceInterval(),
                sv_structure=sv_structure,
            )

            action_name = f"Sensetive({action_name})"
            sv_structure.behavior[0].addBody(
                (action_name, ElementsTypes.ACTION_ELEMENT)
            )

        else:
            generateBodyToAplan(self, child, sv_structure, init_var_name, current_value)


def prepareGenerateExpression(module: Module, expression: str):
    expression = replace_cpp_operators(expression)
    expression = parallelAssignment2Assignment(expression)
    expression = replaceParametrsCalls(module.parametrs, expression)

    return expression


def generate2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Loop_generate_constructContext
):
    generate_name = (
        "GENERATE" + "_" + str(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
    )
    struct = Structure(
        generate_name,
        ctx.getSourceInterval(),
    )
    struct.addProtocol(generate_name, ElementsTypes.GENERATE_ELEMENT)
    initialization = ctx.genvar_initialization().getText()
    initialization = prepareGenerateExpression(self.module, initialization)

    condition = ctx.genvar_expression().getText()
    condition = prepareGenerateExpression(self.module, condition)

    iteration = ctx.genvar_iteration().getText()
    iteration = prepareGenerateExpression(self.module, iteration)
    init_var_name = initialization.split("=")[0]
    exec(initialization)
    while eval(condition):
        current_value = eval(init_var_name)
        generateBodyToAplan(
            self, ctx.generate_block(), struct, init_var_name, current_value
        )
        exec(iteration)
    self.module.structures.addElement(struct)
