from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from classes.tasks import Task
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object, extractParameters, findReturnOrAssignment


def taskOrFunctionDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Task_declarationContext
        | SystemVerilogParser.Function_declarationContext
        | SystemVerilogParser.Class_constructor_declarationContext
    ),
):
    if isinstance(ctx, SystemVerilogParser.Task_declarationContext):
        body = ctx.task_body_declaration()
    elif isinstance(ctx, SystemVerilogParser.Function_declarationContext):
        body = ctx.function_body_declaration()
    elif isinstance(ctx, SystemVerilogParser.Class_constructor_declarationContext):
        body = ctx

    taskOrFunctionBodyDeclaration2AplanImpl(self, body)


def taskOrFunctionBodyDeclaration2AplanImpl(
    self: SV2aplan,
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
        return_var_name = f"return_{identifier}"
        body += ctx.function_statement_or_null()

        task_Type = ElementsTypes.FUNCTION_ELEMENT
    elif isinstance(ctx, SystemVerilogParser.Class_constructor_declarationContext):
        identifier = ""
        if ctx.NEW():
            identifier = "new"
        elif ctx.SUPER():
            identifier = "super"
        body += ctx.function_statement_or_null()
        task_Type = ElementsTypes.CONSTRUCTOR_ELEMENT

    task = Task(identifier, ctx.getSourceInterval(), task_Type)
    if self.module.element_type is ElementsTypes.CLASS_ELEMENT:
        task.parametrs.addElement(
            ActionParametr(
                "object_pointer",
                "var",
            )
        )

    for element in ctx.tf_port_list().tf_port_item():
        port_identifier = element.port_identifier()
        if port_identifier is not None:
            task.parametrs.addElement(
                ActionParametr(
                    port_identifier.getText(),
                    "var",
                )
            )

    task_name = "{0}".format(identifier.upper())

    task_call_name = f"{task_name}"

    task_structure = Structure(
        task_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
    )
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
        names_for_change += self.body2Aplan(
            body_element, task_structure, ElementsTypes.TASK_ELEMENT
        )

    self.inside_the_task = False

    if isinstance(ctx, SystemVerilogParser.Function_body_declarationContext):
        self.inside_the_function = False

    for element in names_for_change:
        self.module.name_change.deleteElement(element)

    self.module.structures.addElement(task_structure)


def taskCall2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Tf_callContext,
    sv_structure: Structure,
    destination_node_array: NodeArray | None = None,
):
    ps_or_hierarchical_tf = ctx.ps_or_hierarchical_tf_identifier()
    hierarchical_tf_identifier = ps_or_hierarchical_tf.hierarchical_tf_identifier()
    object_identifier = None
    if hierarchical_tf_identifier:
        call_identifiers = (
            hierarchical_tf_identifier.hierarchical_identifier().identifier()
        )
        call_identifiers_len = len(call_identifiers)
        task_identifier = call_identifiers[call_identifiers_len - 3].getText()
        object_identifier = call_identifiers[call_identifiers_len - 2].getText()
    else:
        task_identifier = ps_or_hierarchical_tf.getText()

    argument_list = ctx.list_of_arguments().getText()
    (
        argument_list,
        argument_list_with_replaced_names,
    ) = self.prepareExpressionString(argument_list, ElementsTypes.TASK_ELEMENT)

    argument_list_with_replaced_names = self.module.name_change.changeNamesInStr(
        argument_list_with_replaced_names
    )

    argument_list_with_replaced_names = self.module.findAndChangeNamesToAgentAttrCall(
        argument_list_with_replaced_names
    )

    if object_identifier:
        object = self.module.packages_and_objects.findModuleByUniqIdentifier(
            object_identifier
        )
        task = object.tasks.findElement(task_identifier)
        argument_list_with_replaced_names = "{0}, {1}".format(
            object_identifier, argument_list_with_replaced_names
        )
    else:
        task = self.module.tasks.findElement(task_identifier)

    if task is not None:

        if task.element_type == ElementsTypes.TASK_ELEMENT:
            task_call = "{0}".format(task.structure.identifier)

            beh_index = sv_structure.getLastBehaviorIndex()
            copy = task.structure.copy()
            copy.additional_params = argument_list_with_replaced_names
            if beh_index is not None:
                sv_structure.behavior[beh_index].addBody(
                    BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                )
            else:
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                task_call = "B_{0}".format(task.structure.identifier)
                b_index = sv_structure.addProtocol(task_call)
                sv_structure.behavior[b_index].addBody(
                    BodyElement(task_call, copy, ElementsTypes.PROTOCOL_ELEMENT)
                )
        elif task.element_type == ElementsTypes.FUNCTION_ELEMENT:

            objects = self.program.modules.getElementsIE(
                include=ElementsTypes.OBJECT_ELEMENT,
                include_ident_uniq_names=destination_node_array.getElementByIndex(
                    destination_node_array.getLen() - 2
                ).identifier,
                exclude_ident_uniq_name=self.module.ident_uniq_name,
            )

            object_pointer = None
            if objects.getLen() > 0:
                object_pointer = objects.elements[0].ident_uniq_name

            packages = self.module.packages_and_objects.getElementsIE(
                include=ElementsTypes.PACKAGE_ELEMENT,
                exclude_ident_uniq_name=self.module.ident_uniq_name,
            )
            packages += self.program.modules.getElementsIE(
                include=ElementsTypes.CLASS_ELEMENT,
                exclude_ident_uniq_name=self.module.ident_uniq_name,
            )

            functions_list = self.module.tasks.getElementsIE(
                ElementsTypes.FUNCTION_ELEMENT
            ).getElements()
            functions_list += self.module.tasks.getElementsIE(
                ElementsTypes.CONSTRUCTOR_ELEMENT
            ).getElements()

            for package in packages.getElements():
                functions_list += package.tasks.getElementsIE(
                    ElementsTypes.FUNCTION_ELEMENT
                ).getElements()
                functions_list += package.tasks.getElementsIE(
                    ElementsTypes.CONSTRUCTOR_ELEMENT
                ).getElements()

            for function in functions_list:
                if function == task:
                    function_result_var = None
                    if function.element_type is ElementsTypes.CONSTRUCTOR_ELEMENT:
                        function_result_var_for_replase = "{0}".format(
                            self.module.ident_uniq_name
                        )
                    else:
                        function_result_var = "{0}_call_result_{1}".format(
                            function.identifier,
                            Counters_Object.getCounter(CounterTypes.TASK_COUNTER),
                        )
                        function_result_var_for_replase = "{0}.{1}".format(
                            self.module.ident_uniq_name, function_result_var
                        )
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
                            ctx.getSourceInterval(),
                        )
                        sv_structure.elements.addElement(new_decl)
                        decl_unique, decl_index = self.module.declarations.addElement(
                            new_decl
                        )
                        if object_pointer:
                            if len(argument_list_with_replaced_names) > 0:
                                argument_list_with_replaced_names += ", "
                            argument_list_with_replaced_names += object_pointer

                        if function_result_var is not None:
                            if len(argument_list_with_replaced_names) > 0:
                                argument_list_with_replaced_names += ", "
                            argument_list_with_replaced_names += "{0}.{1}".format(
                                self.module.ident_uniq_name, function_result_var
                            )

                        task_call = "{0}".format(task.structure.identifier)
                        beh_index = sv_structure.getLastBehaviorIndex()
                        copy = task.structure.copy()
                        copy.additional_params = argument_list_with_replaced_names
                        if beh_index is not None:
                            sv_structure.behavior[beh_index].addBody(
                                BodyElement(
                                    task_call, copy, ElementsTypes.PROTOCOL_ELEMENT
                                )
                            )
                        else:
                            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                            task_call = "B_{0}".format(task.structure.identifier)
                            b_index = sv_structure.addProtocol(task_call)
                            sv_structure.behavior[b_index].addBody(
                                BodyElement(
                                    task_call, copy, ElementsTypes.PROTOCOL_ELEMENT
                                )
                            )

                        Counters_Object.incrieseCounter(CounterTypes.TASK_COUNTER)
