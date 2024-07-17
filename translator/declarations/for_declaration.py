from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def loopVars2AplanImpl(self: SV2aplan, ctx: SystemVerilogParser.Loop_variablesContext):
    idenifier_list: List[str] = []
    source_interval_list: List[Tuple[int, int]] = []
    for index_variable_identifier in ctx.index_variable_identifier():

        original_identifier = index_variable_identifier.identifier().getText()
        identifier = (
            original_identifier
            + f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        data_type = "int"
        size_expression = data_type
        data_type = DeclTypes.checkType(data_type)
        assign_name = ""
        decl_unique, decl_index = self.module.declarations.addElement(
            Declaration(
                data_type,
                identifier,
                assign_name,
                size_expression,
                0,
                "",
                0,
                index_variable_identifier.getSourceInterval(),
            )
        )

        self.module.name_change.addElement(
            NameChange(
                identifier,
                index_variable_identifier.getSourceInterval(),
                original_identifier,
            )
        )
        idenifier_list.append(identifier)
        source_interval_list.append(index_variable_identifier.getSourceInterval())

    return (idenifier_list, source_interval_list)


def loopVarsDeclarations2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    source_intervals: List[Tuple[int, int]],
):
    assign_names: List[str] = []
    for index, identifier in enumerate(vars_names):
        action_txt = f"{identifier}=0"
        assign_name, source_interval, uniq_action = self.expression2Aplan(
            action_txt,
            ElementsTypes.ASSIGN_ELEMENT,
            source_intervals[index],
        )
        assign_names.append(assign_name)

    return assign_names


def loopVarsToIteration2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    source_intervals: List[Tuple[int, int]],
):
    assign_names: List[str] = []
    for index, identifier in enumerate(vars_names):
        action_txt = f"{identifier}={identifier}+1"
        assign_name, source_interval, uniq_action = self.expression2Aplan(
            action_txt,
            ElementsTypes.ASSIGN_ELEMENT,
            source_intervals[index],
        )
        assign_names.append(assign_name)

    return assign_names


def loopVarsAndArrayIdentifierToCondition2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    ctx: SystemVerilogParser.Ps_or_hierarchical_array_identifierContext,
):
    array_identifier = ctx.hierarchical_array_identifier().getText()
    condition = ""
    decl = self.module.declarations.findElement(array_identifier)
    for index, element in enumerate(vars_names):
        if index != 0:
            condition += "&&"
        condition = "{0}<{1}".format(element, decl.size)
    condition_name, source_interval, uniq_action = self.expression2Aplan(
        condition,
        ElementsTypes.CONDITION_ELEMENT,
        ctx.getSourceInterval(),
    )
    return condition_name


def forInitialization2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.For_initializationContext,
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
        decl_unique, decl_index = self.module.declarations.addElement(
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
        self.module.name_change.addElement(
            NameChange(identifier, expression.getSourceInterval(), original_identifier)
        )

        return identifier
    return None


def forDeclaration2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.For_variable_declarationContext,
):
    assign_name = ""
    data_type = ctx.data_type().getText()
    size_expression = data_type
    if ctx.expression(0) is not None:
        action_txt = (
            f"{ctx.variable_identifier(0).getText()}={ctx.expression(0).getText()}"
        )
        assign_name, source_interval, uniq_action = self.expression2Aplan(
            action_txt,
            ElementsTypes.ASSIGN_ELEMENT,
            ctx.getSourceInterval(),
        )
    data_type = DeclTypes.checkType(data_type)
    identifier = ctx.variable_identifier(0).getText()
    self.module.declarations.addElement(
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
