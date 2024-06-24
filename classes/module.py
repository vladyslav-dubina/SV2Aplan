from utils.utils import generate_module_names
from classes.actions import ActionArray
from classes.parametrs import ParametrArray
from classes.protocols import ProtocolArray
from classes.declarations import DeclarationArray
from classes.structure import StructureArray
from classes.basic import Basic, BasicArray
from classes.module_call import ModuleCallArray
from typing import Tuple


class Module(Basic):
    def __init__(self, identifier: str, source_interval: Tuple[int, int]):
        super().__init__(
            identifier,
            source_interval,
        )
        self.ident_uniq_name, self.number = generate_module_names()
        self.identifierUpper = self.ident_uniq_name.upper()

        # arrays
        self.declarations = DeclarationArray()

        self.actions = ActionArray()

        self.structures = StructureArray()

        self.out_of_block_elements = ProtocolArray()

        self.parametrs = ParametrArray()

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
        protocols = (
            self.out_of_block_elements.getElements()
            + self.structures.getNoAlwaysStructures()
        )
        protocols.sort(key=lambda student: student.sequence)
        for index, element in enumerate(protocols):
            if index != 0:
                main_protocol += ";"
            main_protocol += element.identifier

        if len(main_protocol) > 0:
            main_flag = True
            main_protocol = f"MAIN_{self.identifierUpper} = (" + main_protocol + "),"
            main_protocol_part = f"MAIN_{self.identifierUpper}"
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
            if len(always_list) > 1:
                always_part = "{" + always_part + "}"
            if main_flag:
                always_part += ";"

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
            init_protocol = f"INIT_{self.identifierUpper} = " + init_protocol + ","
            init_protocol_part = f"INIT_{self.identifierUpper}"
            if main_flag or always_flag:
                init_protocol_part += ";"
            if main_flag:
                init_protocol += "\n"
            result = init_protocol + result

        b0 = f"B_{self.identifierUpper} = ({init_protocol_part}{always_part}{main_protocol_part}),"
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

    def __repr__(self):
        return f"ModulesArray(\n{self.elements!r}\n)"
