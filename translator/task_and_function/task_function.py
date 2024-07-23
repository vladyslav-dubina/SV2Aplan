from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.structure import Structure
from classes.tasks import Task
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object, extractParameters


def taskOrFunctionDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Task_declarationContext
        | SystemVerilogParser.Function_declarationContext
    ),
):
    if isinstance(ctx, SystemVerilogParser.Task_declarationContext):
        body = ctx.task_body_declaration()
    elif isinstance(ctx, SystemVerilogParser.Function_declarationContext):
        body = ctx.function_body_declaration()
    taskOrFunctionBodyDeclaration2AplanImpl(self, body)


def taskOrFunctionBodyDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Task_body_declarationContext
        | SystemVerilogParser.Function_body_declarationContext
    ),
):
    if isinstance(ctx, SystemVerilogParser.Task_body_declarationContext):
        identifier = ctx.task_identifier(0).getText()
        body = ctx.statement_or_null(0)
        task_Type = ElementsTypes.TASK_ELEMENT
    elif isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
        identifier = ctx.function_identifier(0).getText()
        return_var_name = f"return_{identifier}"
        body = ctx.function_statement_or_null(0)
        task_Type = ElementsTypes.FUNCTION_ELEMENT

    task = Task(identifier, ctx.getSourceInterval(), task_Type)

    for element in ctx.tf_port_list().tf_port_item():
        task.parametrs.addElement(
            ActionParametr(
                element.port_identifier().getText(),
                "var",
            )
        )

    if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
        task.parametrs.addElement(
            ActionParametr(
                return_var_name,
                "var",
            )
        )

    task_name = "{0}".format(identifier.upper())

    task_call_name = f"{task_name}({task.parametrs})"

    task_structure = Structure(
        task_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
    )
    task.structure = task_structure

    task_structure.addProtocol(task_call_name, ElementsTypes.TASK_ELEMENT)
    self.module.tasks.addElement(task)
    names_for_change = []
    for element in ctx.block_item_declaration():
        names_for_change += self.body2Aplan(
            element, task_structure, ElementsTypes.TASK_ELEMENT
        )

    self.inside_the_task = True

    if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
        task.parametrs.addElement(
            ActionParametr(
                return_var_name,
                "var",
            )
        )
        self.inside_the_function = True

    names_for_change += self.body2Aplan(
        body, task_structure, ElementsTypes.TASK_ELEMENT
    )

    self.inside_the_task = False

    if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
        self.inside_the_function = False

    for element in names_for_change:
        self.module.name_change.deleteElement(element)

    self.module.structures.addElement(task_structure)


def taskCall2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Tf_callContext, sv_structure: Structure
):
    task_identifier = ctx.ps_or_hierarchical_tf_identifier().getText()
    argument_list = ctx.list_of_arguments().getText()
    (
        argument_list,
        argument_list_with_replaced_names,
    ) = self.prepareExpressionString(argument_list, ElementsTypes.TASK_ELEMENT)

    task = self.module.tasks.findElement(task_identifier)
    if task is not None:
        task_call = "{0}({1})".format(
            task.structure.identifier, argument_list_with_replaced_names
        )

        beh_index = sv_structure.getLastBehaviorIndex()

        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                (task_call, ElementsTypes.PROTOCOL_ELEMENT)
            )
        else:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            b_index = sv_structure.addProtocol(
                "B_{}({1})".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER),
                    argument_list_with_replaced_names,
                )
            )
            sv_structure.behavior[b_index].addBody(
                (task_call, ElementsTypes.PROTOCOL_ELEMENT)
            )


def funtionCall2AplanImpl(
    self: SV2aplan,
    task: Task,
    sv_structure: Structure,
    function_result_var: str,
    function_call: str,
    source_interval: Tuple[int, int],
):
    parametrs = extractParameters(function_call, task.identifier)
    parametrs_str = ""

    new_decl = Declaration(
        DeclTypes.INT,
        function_result_var,
        "",
        "",
        0,
        "",
        0,
        source_interval,
    )
    sv_structure.elements.addElement(new_decl)
    decl_unique, decl_index = self.module.declarations.addElement(new_decl)

    for element in parametrs:
        parametrs_str += element
        parametrs_str += ","
    parametrs_str += "{0}.{1}".format(self.module.ident_uniq_name, function_result_var)
    task_call = "{0}({1})".format(task.structure.identifier, parametrs_str)

    beh_index = sv_structure.getLastBehaviorIndex()

    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (task_call, ElementsTypes.PROTOCOL_ELEMENT)
        )
    else:
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        b_index = sv_structure.addProtocol(
            "B_{}({1})".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER),
                parametrs_str,
            )
        )
        sv_structure.behavior[b_index].addBody(
            (task_call, ElementsTypes.PROTOCOL_ELEMENT)
        )

    Counters_Object.incrieseCounter(CounterTypes.TASK_COUNTER)
