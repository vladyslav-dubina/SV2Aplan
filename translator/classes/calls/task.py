from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.protocols import BodyElement
from classes.structure import Structure
from classes.tasks import Task
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class TaskCallTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def translate(
        self,
        ctx: SystemVerilogParser.Tf_callContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ) -> None:
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
                    sv_structure,
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
            argument_list, ElementsTypes.TASK_ELEMENT
        )

        argument_list_with_replaced_names = self.module.declarations.replaseDeclNames(
            argument_list_with_replaced_names
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
            task = object.tasks.findElement(task_identifier)
        else:
            task = self.module.tasks.findElement(task_identifier)
            if task is None:
                packages = self.module.packages_and_objects.getElementsIE(
                    include=ElementsTypes.PACKAGE_ELEMENT,
                    exclude_ident_uniq_name=self.module.ident_uniq_name,
                )
                for element in packages.getElements():
                    task = element.tasks.findElement(task_identifier)
                    if task is not None:
                        break
        self._translator_ptr.getTranslator("task_call").createCall(
            task,
            sv_structure,
            destination_node_array,
            object_identifier,
            argument_list_with_replaced_names,
            ctx.getSourceInterval(),
        )

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def createCall(
        self,
        task: Task | None,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
        object_identifier: str | None = None,
        arguments: str = "",
        source_interval: Tuple[int, int] = (0, 0),
    ) -> None:
        if task is not None:
            if task.element_type == ElementsTypes.TASK_ELEMENT:
                task_call = "{0}".format(task.structure.identifier)

                beh_index = sv_structure.getLastBehaviorIndex()
                copy = task.structure.copy()
                copy.additional_params = arguments
                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )
                else:
                    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                    task_call = "B_{0}".format(task.structure.identifier)
                    b_index = sv_structure.addProtocol(
                        task_call,
                        inside_the_task=(
                            self.inside_the_task or self.inside_the_function
                        ),
                    )
                    sv_structure.behavior[b_index].addBody(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )
            elif task.element_type == ElementsTypes.FUNCTION_ELEMENT:

                function_result_var = None

                if task.findReturnParam():
                    function_result_var = "{0}_call_result_{1}".format(
                        task.identifier,
                        Counters_Object.getCounter(CounterTypes.TASK_COUNTER),
                    )
                    if destination_node_array:
                        node_index = destination_node_array.addElement(
                            Node(
                                function_result_var,
                                (0, 0),
                                ElementsTypes.IDENTIFIER_ELEMENT,
                            )
                        )
                        node = destination_node_array.getElementByIndex(node_index)
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
                    sv_structure.elements.addElement(new_decl)
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
                beh_index = sv_structure.getLastBehaviorIndex()
                copy = task.structure.copy()
                copy.additional_params = arguments
                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )
                else:
                    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                    task_call = "B_{0}".format(task.structure.identifier)
                    b_index = sv_structure.addProtocol(
                        task_call,
                        inside_the_task=(
                            self.inside_the_task or self.inside_the_function
                        ),
                    )
                    sv_structure.behavior[b_index].addBody(
                        BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                    )

                Counters_Object.incrieseCounter(CounterTypes.TASK_COUNTER)
