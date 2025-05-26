from typing import List
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.element_types import ElementsTypes
from classes.parametrs import Parametr
from classes.protocols import Protocol
from classes.structure import Structure
from classes.tasks import Task
from translator.classes.base_translator import BaseTranslator


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
        task = Task(identifier, ctx.getSourceInterval(), task_Type)
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

        task_structure = Structure(
            task_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
        )
        if self.module.input_parametrs is not None:
            task.parametrs += self.module.input_parametrs

        task_structure.parametrs = task.parametrs

        task.structure = task_structure

        task_protocol = Protocol(task_call_name, ElementsTypes.TASK_ELEMENT)
        task_protocol.parametrs = task.parametrs

        task_structure.behavior.append(task_protocol)
        self.module.tasks.addElement(task)
        names_for_change = []
        self.inside_the_task = True

        if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
            self.inside_the_function = True

        for body_element in body:
            names_for_change += self._translator_ptr.body2Aplan(
                body_element, task_structure, ElementsTypes.TASK_ELEMENT
            )

        self.inside_the_task = False

        if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
            self.inside_the_function = False

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
