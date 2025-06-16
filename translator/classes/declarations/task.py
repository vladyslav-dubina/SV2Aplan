from typing import List
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.parametrs import Parametr
from classes.protocols import Protocol
from classes.structure import Structure
from classes.tasks import Task, TaskStmt
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class TaskBodyDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Task_body_declarationContext
            | SystemVerilogParser.Function_body_declarationContext
            | SystemVerilogParser.Class_constructor_declarationContext
        ),
    ) -> None:
        (body, identifier, task_Type) = self._getBody(ctx)
        task = Task(
            identifier,
            ctx.getSourceInterval(),
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER),
            task_Type,
        )
        if self.module.element_type is ElementsTypes.CLASS_ELEMENT:
            task.parametrs.addElement(
                Parametr(
                    "object_pointer",
                    "var",
                )
            )

        for element in ctx.tf_port_list().tf_port_item():
            port_identifier = element.port_identifier()
            if port_identifier is not None:
                task.parametrs.addElement(
                    Parametr(
                        port_identifier.getText(),
                        "var",
                    )
                )
        task_name = "{0}".format(identifier.upper())

        task_call_name = f"{task_name}"

        task_structure = TaskStmt(
            task_call_name,
            (0, 0),
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER),
        )

        task_structure.inside_the_task = self.inside_the_task

        if self.module.input_parametrs is not None:
            task.parametrs += self.module.input_parametrs

        task_structure.parametrs = task.parametrs

        task.structure = task_structure

        task_protocol = Protocol(
            "{0}_{1}".format(task_call_name, task_structure.number),
            ElementsTypes.TASK_ELEMENT,
        )

        task_protocol.parametrs = task.parametrs

        task_structure.behavior.append(task_protocol)

        self.module.tasks.addElement(task)
        task_structure.inside_the_task
        names_for_change = []

        self._translator_ptr._structure_pointer_list.addElement(task_structure)

        for body_element in body:
           # print("start")
            names_for_change += self._translator_ptr.body2Aplan(
                body_element, task_structure
            )

        Counters_Object.incriese(CounterTypes.STRUCT_COUNTER)

        self.module.structures.addElement(task_structure)

    def _getBody(
        self,
        ctx: (
            SystemVerilogParser.Task_body_declarationContext
            | SystemVerilogParser.Function_body_declarationContext
            | SystemVerilogParser.Class_constructor_declarationContext
        ),
    ):
        body = []
        body += ctx.block_item_declaration()
        if isinstance(ctx, SystemVerilogParser.Task_body_declarationContext):
            identifier = ctx.task_identifier(0).getText()
            body += ctx.statement_or_null()
            task_Type = ElementsTypes.TASK_ELEMENT
        elif isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
            identifier = ctx.function_identifier(0).getText()
            body += ctx.function_statement_or_null()

            task_Type = ElementsTypes.FUNCTION_ELEMENT
        elif isinstance(ctx, SystemVerilogParser.Class_constructor_declarationContext):
            identifier = ""
            if ctx.NEW():
                identifier = "new"
            elif ctx.SUPER():
                identifier = "super"
            body += ctx.function_statement_or_null()
            task_Type = ElementsTypes.FUNCTION_ELEMENT

        return (body, identifier, task_Type)
