from typing import List, Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_precondition import ActionPreconditionArray
from classes.counters import CounterTypes
from classes.declarations import AplanDeclType
from classes.element_types import ElementsTypes
from classes.module_call import ModuleCall
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement, Protocol
from program.program import Program
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replace_filename
from utils.utils import Color, Counters_Object, printWithColor
from translator.translation_mngr import TranslationManager


class ModuleCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Module_instantiationContext) -> None:
        destination_identifier = ctx.module_identifier().getText()
        object_name = ""
        hierarchy = ctx.hierarchical_instance(0)
        if hierarchy is not None:
            object_name = hierarchy.name_of_instance().getText()

        parametrs = ctx.parameter_value_assignment()
        if parametrs is not None:
            parametrs = parametrs.getText()
        else:
            parametrs = ""

        parametrs = ctx.parameter_value_assignment()
        if parametrs is not None:
            parametrs = parametrs.getText()
        else:
            parametrs = ""

        module_call = ModuleCall(
            destination_identifier,
            object_name,
            self.module.identifier,
            destination_identifier,
            parametrs,
            self.module.value_parametrs,
        )
        call_module_name = object_name

        try:
            previous_file_path = self._program.file_path
            file_path = replace_filename(
                self._program.file_path, f"{destination_identifier}.sv"
            )
            file_data = self._program.readFileData(file_path)
            translation_mngr = TranslationManager()
            translation_mngr.setUp(file_data)
            translation_mngr.startTranslate(module_call)
        except Exception as e:

            self._program.module_calls.addElement(module_call)

        call_module = self._program.modules.findModuleByUniqIdentifier(call_module_name)
        if call_module is None:
            call_module = self._program.module_calls.findModuleByUniqIdentifier(
                call_module_name
            )
        if call_module.element_type != ElementsTypes.INTERFACE_ELEMENT:
            self._program.file_path = previous_file_path
            self.assign(ctx, call_module_name, destination_identifier)
            Counters_Object.incriese(CounterTypes.B_COUNTER)
            call_b = "MODULE_CALL_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_call = Protocol(
                call_b, ctx.getSourceInterval(), ElementsTypes.MODULE_CALL_ELEMENT
            )
            struct_call.addBody(
                BodyElement(
                    identifier=f"B_{call_module_name.upper()}",
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                )
            )
            self.module.out_of_block_elements.addElement(struct_call)

    def assign(
        self,
        ctx: SystemVerilogParser.Module_instantiationContext,
        destination_module_name: str,
        destination_identifier: str,
    ):
        for hierarchical_instance in ctx.hierarchical_instance():
            instance = hierarchical_instance.name_of_instance().getText()
            index = instance.find("core")
            if index != -1:
                Counters_Object.incriese(CounterTypes.B_COUNTER)
                call_assign_b = "MODULE_ASSIGN_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                struct_call_assign = Protocol(
                    call_assign_b,
                    ctx.getSourceInterval(),
                    ElementsTypes.MODULE_ASSIGN_ELEMENT,
                )

                for (
                    order_port_connection
                ) in (
                    hierarchical_instance.list_of_port_connections().ordered_port_connection()
                ):
                    printWithColor(f"Unhandled case for module call", Color.RED)

                assign_str_list: List[str] = []
                assign_arr_str_list: List[
                    Tuple[
                        str,
                        ParametrArray,
                        ActionPreconditionArray,
                    ]
                ] = []
                for (
                    named_port_connection
                ) in (
                    hierarchical_instance.list_of_port_connections().named_port_connection()
                ):
                    destination_var_name = (
                        named_port_connection.port_identifier().getText()
                    )
                    source_var_name = named_port_connection.expression().getText()
                    assign_str = "{0}.{1}={2}.{3}".format(
                        destination_module_name,
                        destination_var_name,
                        self.module.ident_uniq_name,
                        source_var_name,
                    )
                    decl = self.module.declarations.findDeclWithDimentionByName(
                        source_var_name
                    )
                    if decl is None:
                        assign_str_list.append(assign_str)
                    else:
                        precond_array: NodeArray = NodeArray(
                            ElementsTypes.PRECONDITION_ELEMENT
                        )
                        param_array: ParametrArray = ParametrArray()
                        uniq, param_index = param_array.addElement(
                            Parametr(
                                decl.getName(),
                                decl.getAplanDecltype(AplanDeclType.PARAMETRS),
                            )
                        )
                        param_array.generateUniqNamesForParamets()
                        precond_array.addElement(
                            Node("0", (0, 0), ElementsTypes.NUMBER_ELEMENT)
                        )
                        precond_array.addElement(
                            Node("<=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                        )
                        param = param_array.getElementByIndex(param_index)
                        precond_array.addElement(
                            Node(
                                f"{param.unique_identifier}",
                                (0, 0),
                                ElementsTypes.IDENTIFIER_ELEMENT,
                            )
                        )
                        precond_array.addElement(
                            Node("<", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                        )
                        precond_array.addElement(
                            Node(
                                f"{decl.dimension_size}",
                                (0, 0),
                                ElementsTypes.NUMBER_ELEMENT,
                            )
                        )
                        assign_str = "{0}.{1}[{4}] = {2}.{3}[{4}]".format(
                            destination_module_name,
                            destination_var_name,
                            self.module.ident_uniq_name,
                            source_var_name,
                            param.unique_identifier,
                        )
                        assign_arr_str_list.append(
                            (
                                assign_str,
                                param_array,
                                precond_array,
                            )
                        )
                obj_def = f"{destination_identifier.upper()}#{destination_module_name};{self.module.identifier_upper}#{self.module.ident_uniq_name}"
                (
                    action_pointer,
                    action_name,
                    source_interval,
                    uniq_action,
                ) = self._translator_ptr.getTranslator("expr").actionFromNodeStr(
                    assign_str_list,
                    ctx.getSourceInterval(),
                    ElementsTypes.ASSIGN_FOR_CALL_ELEMENT,
                    input_parametrs=(obj_def, None, None),
                )

                action_2 = ""
                for element in assign_arr_str_list:
                    expression, parametrs, predicates = element
                    (
                        action_pointer_2,
                        action_name_2,
                        source_interval,
                        uniq_action,
                    ) = self._translator_ptr.getTranslator("expr").actionFromNodeStr(
                        expression,
                        ctx.getSourceInterval(),
                        ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT,
                        input_parametrs=(
                            obj_def,
                            parametrs,
                            predicates,
                        ),
                    )
                    if uniq_action:
                        action_2 += f".Sensetive({action_name_2})"

                action_name = f"Sensetive({action_name}){action_2}"
                struct_call_assign.addBody(
                    BodyElement(
                        action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )

                self.module.out_of_block_elements.addElement(struct_call_assign)

    def resolve(self, identifier):
        local_module_call: ModuleCall = None
        uniq_name = identifier
        if self.module_call is not None:
            local_module_call = self.module_call
        else:
            local_module_call = Program().module_calls.findElement(identifier)
        if local_module_call is not None:
            if identifier == local_module_call.identifier:
                identifier = local_module_call.identifier
                uniq_name = local_module_call.object_name

        return (identifier, uniq_name)
