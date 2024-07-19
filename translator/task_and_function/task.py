from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from classes.structure import Structure
from classes.tasks import Task
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def taskDeclaration2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Task_declarationContext
):
    taskBodyDeclaration2AplanImpl(self, ctx.task_body_declaration())


def taskBodyDeclaration2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Task_body_declarationContext
):
    identifier = ctx.task_identifier(0).getText()

    task = Task(identifier, ctx.getSourceInterval())

    for element in ctx.tf_port_list().tf_port_item():
        task.parametrs.addElement(
            ActionParametr(
                element.port_identifier().getText(),
                "var",
            )
        )

    task_name = "{0}".format(identifier.upper())

    task_call_name = f"{task_name}({task.parametrs})"

    task_structure = Structure(
        task_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
    )

    task_structure.addProtocol(task_call_name, ElementsTypes.TASK_ELEMENT)
    self.module.tasks.addElement(task)
    names_for_change = []
    for element in ctx.block_item_declaration():
        names_for_change += self.body2Aplan(
            element, task_structure, ElementsTypes.TASK_ELEMENT
        )

    self.inside_the_task = True
    names_for_change += self.body2Aplan(
        ctx.statement_or_null(0), task_structure, ElementsTypes.TASK_ELEMENT
    )
    self.inside_the_task = False

    for element in names_for_change:
        self.module.name_change.deleteElement(element)

    task.structure = task_structure
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
