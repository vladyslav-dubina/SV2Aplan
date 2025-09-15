from pathlib import Path
from typing import List, Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.action_precondition import ActionPreconditionArray
from Core.src.classes.declarations import AplanDeclType
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.design_unit_call import DesignUnitCall
from Core.src.classes.node import Node, NodeArray
from Core.src.classes.parametrs import Parametr, ParametrArray
from Core.src.classes.protocols import BodyElement, Protocol
from Core.src.program.program import Program
from translator.classes.base_translator import BaseTranslator
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

        design_unit_call = DesignUnitCall(
            destination_identifier,
            object_name,
            self.design_unit.identifier,
            destination_identifier,
            parametrs,
            self.design_unit.value_parametrs,
        )
        call_design_unit_name = object_name

        previous_file_path: Path = None
        try:
            previous_file_path: Path = self._program.file_path
            file_path: Path = self.file_mngr.replaceFilename(
                self._program.file_path, f"{destination_identifier}.sv"
            )
            translation_mngr = TranslationManager()
            translation_mngr.setup(file_path)
            translation_mngr.translate(design_unit_call)
        except Exception as e:
            self._program.design_units_calls.addElement(design_unit_call)

        call_design_unit = self._program.design_units.findModuleByUniqIdentifier(
            call_design_unit_name
        )
        if call_design_unit is None:
            call_design_unit = (
                self._program.design_units_calls.findModuleByUniqIdentifier(
                    call_design_unit_name
                )
            )
        if call_design_unit.element_type != ElementsTypes.INTERFACE_ELEMENT:
            self._program.file_path = previous_file_path
            self.assign(ctx, call_design_unit_name, destination_identifier)
            self.counters.incriese(self.counters.types.B_COUNTER)
            call_b = "MODULE_CALL_B_{}".format(
                self.counters.get(self.counters.types.B_COUNTER)
            )
            struct_call = Protocol(
                call_b, ctx.getSourceInterval(), ElementsTypes.MODULE_CALL_ELEMENT
            )
            struct_call.addBodyElement(
                BodyElement(
                    identifier=f"B_{call_design_unit_name.upper()}",
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                )
            )
            self.design_unit.out_of_block_elements.addElement(struct_call)

    def assign(
        self,
        ctx: SystemVerilogParser.Module_instantiationContext,
        destination_design_unit_name: str,
        destination_identifier: str,
    ):
        for hierarchical_instance in ctx.hierarchical_instance():
            instance = hierarchical_instance.name_of_instance().getText()
            index = instance.find("core")
            if index != -1:
                self.counters.incriese(self.counters.types.B_COUNTER)
                call_assign_b = "MODULE_ASSIGN_B_{}".format(
                    self.counters.get(self.counters.types.B_COUNTER)
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
                    self.logger.warning("Unhandled case for design_unit call")

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
                        destination_design_unit_name,
                        destination_var_name,
                        self.design_unit.ident_uniq_name,
                        source_var_name,
                    )
                    decl = self.design_unit.declarations.findDeclWithDimentionByName(
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
                            destination_design_unit_name,
                            destination_var_name,
                            self.design_unit.ident_uniq_name,
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
                obj_def = f"{destination_identifier.upper()}#{destination_design_unit_name};{self.design_unit.identifier_upper}#{self.design_unit.ident_uniq_name}"
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
                struct_call_assign.addBodyElement(
                    BodyElement(
                        action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )

                self.design_unit.out_of_block_elements.addElement(struct_call_assign)

    def resolve(self, identifier):
        local_design_unit_call: DesignUnitCall = None
        uniq_name = f"{identifier}_{self.utils.generate_unique_short_id(identifier)}"
        if self.design_unit_call is not None:
            local_design_unit_call = self.design_unit_call
        else:
            local_design_unit_call = Program().design_units_calls.getElement(identifier)
        if local_design_unit_call is not None:
            if identifier == local_design_unit_call.identifier:
                identifier = local_design_unit_call.identifier
                uniq_name = local_design_unit_call.object_name

        return (identifier, uniq_name)
