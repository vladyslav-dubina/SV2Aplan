from classes.processed import ProcessedElementArray
from classes.actions import ActionArray
from classes.parametrs import ParametrArray
from classes.protocols import ProtocolArray
from classes.declarations import DeclarationArray
from classes.structure import StructureArray
from classes.basic import Basic, BasicArray
from classes.module_call import ModuleCallArray
from classes.name_change import NameChangeArray
from classes.element_types import ElementsTypes
from typing import Tuple
import re


class Module(Basic):
    def __init__(
        self, identifier: str, source_interval: Tuple[int, int], ident_uniq_name
    ):
        super().__init__(
            identifier.upper(),
            source_interval,
        )
        self.ident_uniq_name = ident_uniq_name
        self.identifier_upper = self.identifier.upper()
        self.ident_uniq_name_upper = self.ident_uniq_name.upper()
        # arrays
        self.declarations = DeclarationArray()

        self.actions = ActionArray()

        self.structures = StructureArray()

        self.out_of_block_elements = ProtocolArray()

        self.parametrs = ParametrArray()

        self.name_change = NameChangeArray()

        self.processed_elements = ProcessedElementArray()

    def findAndChangeNamesToAgentAttrCall(self, input: str):
        for elem in self.declarations.getElements():
            input = re.sub(
                r"\b{}\b".format(re.escape(elem.identifier)),
                "{}.{}".format(self.ident_uniq_name, elem.identifier),
                input,
            )
        return input

    def isIncludeOutOfBlockElements(self):
        if len(self.out_of_block_elements.getElements()) > 0:
            return True
        return False

    def getBehInitProtocols(self):
        result = ""

        # MAIN PROTOCOL
        main_protocol = ""
        main_protocol_part = ""
        main_flag = False
        protocols = self.out_of_block_elements.getElements()
        protocols.sort(key=lambda student: student.sequence)
        for index, element in enumerate(protocols):
            if index != 0:
                prev_element = protocols[index - 1]

                if element.element_type == ElementsTypes.MODULE_CALL_ELEMENT:
                    main_protocol += ";"
                else:
                    main_protocol += " || "

                if (
                    prev_element.element_type
                    == ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT
                ) and (
                    element.element_type == ElementsTypes.MODULE_CALL_ELEMENT
                    or element.element_type == ElementsTypes.MODULE_ASSIGN_ELEMENT
                ):
                    main_protocol += "("

            main_protocol += element.identifier

            if index + 1 < len(protocols):
                if (
                    protocols[index + 1].element_type
                    == ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT
                ) and (
                    element.element_type == ElementsTypes.MODULE_CALL_ELEMENT
                    or element.element_type == ElementsTypes.MODULE_ASSIGN_ELEMENT
                ):
                    main_protocol += ")"

        if len(main_protocol) > 0:
            main_flag = True
            main_protocol = (
                f"MAIN_{self.ident_uniq_name_upper} = (" + main_protocol + "),"
            )
            main_protocol_part = f"MAIN_{self.ident_uniq_name_upper}"
            result += main_protocol

        # ALWAYS PART
        always_list = self.structures.getAlwaysList()
        always_part = ""
        always_flag = False

        for index, element in enumerate(always_list):
            if index != 0:
                always_part += " || "
            always_part += element.getSensetiveForB0()

        if len(always_part) > 0:
            always_flag = True
            if main_flag:
                always_part += " || "

        structs = self.structures.getNoAlwaysStructures()
        struct_part = ""
        struct_flag = False
        for index, element in enumerate(structs):
            if index != 0:
                struct_part += " || "
            struct_part += element.identifier

        if len(struct_part) > 0:
            struct_flag = True
            if always_flag:
                struct_part += " || "

        # INIT PROTOCOL
        init_protocol = ""
        init_protocol_part = ""
        init_protocols_array = self.declarations.getDeclarationsWithExpressions()
        init_flag = False

        init_protocols_array.sort(key=lambda student: student.sequence)
        for index, element in enumerate(init_protocols_array):
            if index != 0:
                init_protocol += "."
            init_protocol += element.expression

        if len(init_protocol) > 0:
            init_flag = True
            init_protocol = (
                f"INIT_{self.ident_uniq_name_upper} = " + init_protocol + ","
            )
            init_protocol_part = f"INIT_{self.ident_uniq_name_upper}"
            if main_flag or always_flag or struct_flag:
                init_protocol_part += " || "
            if main_flag:
                init_protocol += "\n"
            result = init_protocol + result

        b0 = f"B_{self.ident_uniq_name_upper} = {{{init_protocol_part}{struct_part}{always_part}{main_protocol_part}}},"
        if main_flag or init_flag:
            b0 += "\n"
        result = b0 + result
        return result

    def __repr__(self):
        return f"\tModule({self.identifier!r}\n)"


class ModuleArray(BasicArray):
    def __init__(self):
        super().__init__(Module)
        self.module_instantiations: ModuleCallArray = ModuleCallArray()

    def findModuleByUтiqIdentifier(self, ident_uniq_name: str):
        for element in self.elements:
            if element.ident_uniq_name == ident_uniq_name:
                return element
        return None

    def __repr__(self):
        return f"ModulesArray(\n{self.elements!r}\n)"
