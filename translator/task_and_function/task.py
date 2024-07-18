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


# Need undestand how how to find out that this action is in the middle of a task and it needs parameters
def taskBodyDeclaration2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Task_body_declarationContext
):
    identifier = ctx.task_identifier(0).getText()

    parametrs = []

    task = Task(identifier, ctx.getSourceInterval())

    for element in ctx.tf_port_list().tf_port_item():
        parametrs.append(element.port_identifier().getText())

    task_name = "{0}_{1}".format(
        identifier.upper(), Counters_Object.getCounter(CounterTypes.TASK_COUNTER)
    )

    task.parametrs = parametrs

    task_structure = Structure(task_name, ctx.getSourceInterval())

    task_structure.addProtocol(task_name)
    self.module.tasks.addElement(task)
    names_for_change = []
    for element in ctx.block_item_declaration():
        names_for_change += self.body2Aplan(
            element, task_structure, ElementsTypes.TASK_ELEMENT
        )

    names_for_change += self.body2Aplan(
        ctx.statement_or_null(0), task_structure, ElementsTypes.TASK_ELEMENT
    )

    for element in names_for_change:
        self.module.name_change.deleteElement(element)

    task.structure = task_structure
    Counters_Object.incrieseCounter(CounterTypes.TASK_COUNTER)
