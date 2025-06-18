from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node, NodeArray
from AppModule.app.classes.protocols import BodyElement
from AppModule.app.classes.tasks import Task
from translator.classes.base_translator import BaseTranslator


class TaskCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Tf_callContext,
    ) -> None:
        self.findStruct()
        ps_or_hierarchical_tf: (
            SystemVerilogParser.Ps_or_hierarchical_tf_identifierContext
        ) = ctx.ps_or_hierarchical_tf_identifier()
        hierarchical_tf_identifier: (
            SystemVerilogParser.Hierarchical_tf_identifierContext
        ) = ps_or_hierarchical_tf.hierarchical_tf_identifier()
        object_identifier = None
        argument_list = ctx.list_of_arguments().getText()
        if hierarchical_tf_identifier:
            call_identifiers: SystemVerilogParser.Hierarchical_identifierContext = (
                hierarchical_tf_identifier.hierarchical_identifier().identifier()
            )
            call_identifiers_len = len(call_identifiers)
            task_identifier = call_identifiers[call_identifiers_len - 3].getText()
            object_identifier = call_identifiers[call_identifiers_len - 2].getText()
            if task_identifier == "push_back":
                self._translator_ptr.translate(
                    "push_back",
                    self.last_struct,
                    task_identifier,
                    object_identifier,
                    ctx.list_of_arguments(),
                    ctx.getSourceInterval(),
                )
                return
        else:
            task_identifier = ps_or_hierarchical_tf.getText()

        (
            argument_list,
            argument_list_with_replaced_names,
        ) = self._translator_ptr.getTranslator("expr").prepareExpressionString(
            argument_list
        )

        argument_list_with_replaced_names = (
            self.module.findAndChangeNamesToAgentAttrCall(
                argument_list_with_replaced_names
            )
        )

        if object_identifier:
            object = self.module.packages_and_objects.findModuleByUniqIdentifier(
                object_identifier
            )
            task = object.tasks.getElement(task_identifier)
        else:
            task = self.module.tasks.getElement(task_identifier)
            if task is None:
                packages = self.module.packages_and_objects.getElementsIE(
                    include=ElementsTypes.PACKAGE_ELEMENT,
                    exclude_ident_uniq_name=self.module.ident_uniq_name,
                )
                for element in packages.getElements():
                    task = element.tasks.getElement(task_identifier)
                    if task is not None:
                        break

        self.createCall(
            task,
            object_identifier,
            argument_list_with_replaced_names,
            ctx.getSourceInterval(),
        )

    def createCall(
        self,
        task: Task | None,
        object_identifier: str | None = None,
        arguments: str = "",
        source_interval: Tuple[int, int] = (0, 0),
    ) -> None:
        if task is not None:
            self.findStruct()

            if task.element_type == ElementsTypes.TASK_ELEMENT:
                task_call = "{0}".format(task.structure.identifier)

                beh_index = self.last_struct.getLastBehaviorIndex()
                copy = task.structure.copy()
                copy.additional_params = arguments

                if beh_index is not None:
                    self.last_struct.behavior[beh_index].addBodyElement(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )

                else:
                    self.counters.incriese(self.counters.types.B_COUNTER)
                    task_call = "B_{0}".format(task.structure.identifier)
                    beh_index = self.last_struct.addProtocol(
                        task_call,
                        inside_the_task=self.inside_the_task,
                    )
                    self.last_struct.behavior[beh_index].addBodyElement(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )

            elif task.element_type == ElementsTypes.FUNCTION_ELEMENT:
                function_result_var = None
                if task.findReturnParam():
                    function_result_var = "{0}_{1}_call_result".format(
                        task.identifier, task.number
                    )
                    if self.last_node_array:
                        node_index = self.last_node_array.addElement(
                            Node(
                                function_result_var,
                                (0, 0),
                                ElementsTypes.IDENTIFIER_ELEMENT,
                            )
                        )
                        node = self.last_node_array.getElementByIndex(node_index)
                        node.module_name = self.module.ident_uniq_name

                if function_result_var is not None:
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
                    self.last_struct.elements.addElement(new_decl)
                    decl_unique, decl_index = self.module.declarations.addElement(
                        new_decl
                    )

                if object_identifier:
                    if len(arguments) > 0:
                        arguments = ", " + arguments
                    arguments = object_identifier + arguments

                if function_result_var is not None:
                    if len(arguments) > 0:
                        arguments += ", "
                    arguments += "{0}.{1}".format(
                        self.module.ident_uniq_name, function_result_var
                    )

                task_call = "{0}".format(task.structure.identifier)
                beh_index = self.last_struct.getLastBehaviorIndex()
                copy = task.structure.copy()
                copy.additional_params = arguments
                if beh_index is not None:
                    self.last_struct.behavior[beh_index].addBodyElement(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )
                else:
                    self.counters.incriese(self.counters.types.B_COUNTER)
                    task_call = "B_{0}".format(task.structure.identifier)
                    b_index = self.last_struct.addProtocol(
                        task_call,
                        inside_the_task=self.inside_the_task,
                    )
                    self.last_struct.behavior[b_index].addBodyElement(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )
