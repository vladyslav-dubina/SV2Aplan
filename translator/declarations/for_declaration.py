from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from classes.module import Module
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def forInitializationToApan(
    ctx: SystemVerilogParser.For_initializationContext,
    module: Module,
):
    assign_name = ""
    expression = ctx.for_variable_declaration(0)
    if expression is not None:
        original_identifier = expression.variable_identifier(0).getText()
        identifier = (
            original_identifier
            + f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        data_type = expression.data_type().getText()
        size_expression = data_type
        data_type = DeclTypes.checkType(data_type)
        decl_unique, decl_index = module.declarations.addElement(
            Declaration(
                data_type,
                identifier,
                assign_name,
                size_expression,
                0,
                "",
                0,
                expression.getSourceInterval(),
            )
        )
        module.name_change.addElement(
            NameChange(identifier, expression.getSourceInterval(), original_identifier)
        )

        return identifier
    return None


def forDeclarationToApan(
    ctx: SystemVerilogParser.For_variable_declarationContext,
    module: Module,
):
    assign_name = ""
    data_type = ctx.data_type().getText()
    size_expression = data_type
    sv2aplan = SV2aplan(module)
    if ctx.expression(0) is not None:
        action_txt = (
            f"{ctx.variable_identifier(0).getText()}={ctx.expression(0).getText()}"
        )
        assign_name, source_interval = sv2aplan.expression2Aplan(
            action_txt,
            ElementsTypes.ASSIGN_ELEMENT,
            ctx.getSourceInterval(),
        )
    data_type = DeclTypes.checkType(data_type)
    identifier = ctx.variable_identifier(0).getText()
    module.declarations.addElement(
        Declaration(
            data_type,
            identifier,
            assign_name,
            size_expression,
            0,
            "",
            0,
            ctx.getSourceInterval(),
        )
    )
