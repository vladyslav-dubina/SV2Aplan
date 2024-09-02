from classes.parametrs import ParametrArray
from classes.processed import ProcessedElementArray
from classes.actions import ActionArray
from classes.value_parametrs import ValueParametrArray
from classes.protocols import ProtocolArray
from classes.declarations import DeclTypes, DeclarationArray
from classes.structure import StructureArray
from classes.basic import Basic, BasicArray
from classes.module_call import ModuleCallArray
from classes.name_change import NameChangeArray
from classes.element_types import ElementsTypes
from typing import List, Tuple
import re

from classes.tasks import TaskArray


class Module(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        ident_uniq_name,
        element_type: ElementsTypes = ElementsTypes.MODULE_ELEMENT,
    ):
        super().__init__(identifier.upper(), source_interval, element_type)
        self.ident_uniq_name = ident_uniq_name
        self.identifier_upper = self.identifier.upper()
        self.ident_uniq_name_upper = self.ident_uniq_name.upper()
        # arrays
        self.declarations: DeclarationArray = DeclarationArray()

        self.actions: ActionArray = ActionArray()

        self.structures: StructureArray = StructureArray()

        self.out_of_block_elements: ProtocolArray = ProtocolArray()

        self.value_parametrs: ValueParametrArray = ValueParametrArray()

        self.input_parametrs: ParametrArray = ParametrArray()

        self.name_change: NameChangeArray = NameChangeArray()

        self.processed_elements: ProcessedElementArray = ProcessedElementArray()

        self.tasks: TaskArray = TaskArray()

        self.packages_and_objects: ModuleArray = ModuleArray()

    def copyPart(self):
        module = Module(
            self.identifier,
            self.source_interval,
            self.ident_uniq_name,
            self.element_type,
        )
        module.declarations = self.declarations
        module.actions = self.actions
        module.structures = self.structures
        module.out_of_block_elements = self.out_of_block_elements
        module.value_parametrs = self.value_parametrs
        module.name_change = self.name_change
        module.processed_elements = self.processed_elements
        module.tasks = self.tasks
        module.packages_and_objects = self.packages_and_objects

        return module

    def copy(self):
        module = Module(
            self.identifier,
            self.source_interval,
            self.ident_uniq_name,
            self.element_type,
        )

        module.declarations = self.declarations.copy()
        module.actions = self.actions.copy()
        module.structures = self.structures.copy()
        module.structures.updateLinks(module)
        module.out_of_block_elements = self.out_of_block_elements.copy()
        self.out_of_block_elements.updateLinks(module)
        module.value_parametrs = self.value_parametrs.copy()
        module.name_change = self.name_change.copy()
        module.processed_elements = self.processed_elements.copy()
        module.tasks = self.tasks.copy()
        module.packages_and_objects = self.packages_and_objects.copy()

        return module

    def findAndChangeNamesToAgentAttrCall(self, input: str, packages=None):
        if self.element_type is ElementsTypes.CLASS_ELEMENT:
            ident_uniq = "object_pointer"
        else:
            ident_uniq = self.ident_uniq_name

        for elem in self.declarations.getElements():
            input = re.sub(
                r"\b{}\b".format(re.escape(elem.identifier)),
                "{}.{}".format(ident_uniq, elem.identifier),
                input,
            )

        if packages is not None:
            for package in packages:
                if self.element_type is ElementsTypes.CLASS_ELEMENT:
                    package_ident_uniq_name = "object_pointer"
                else:
                    package_ident_uniq_name = package.ident_uniq_name
                for elem in package.declarations.getElements():
                    input = re.sub(
                        r"\b{}\b".format(re.escape(elem.identifier)),
                        "{}.{}".format(package_ident_uniq_name, elem.identifier),
                        input,
                    )

        return input

    def isIncludeOutOfBlockElements(self):
        if len(self.out_of_block_elements.getElements()) > 0:
            return True
        return False

    def findElementByIdentifier(self, identifier: str):
        result = []
        for element in self.declarations.getElements():
            if element.identifier == identifier:
                result.append(element)
                if (
                    element.data_type is not DeclTypes.ENUM_TYPE
                    and len(element.expression) > 0
                ):
                    result.append(element.action)

        for element in self.tasks.getElements():
            if element.identifier == identifier:
                result.append(element)
                result.append(element.structure)
                for struct_element in element.structure.elements.getElements():
                    result.append(struct_element)

        for element in self.value_parametrs.getElements():
            if element.identifier == identifier:
                result.append(element)

        return result

    def getInputParametrs(self):
        result = ""
        if self.input_parametrs.getLen() > 0:
            result = f"({str(self.input_parametrs)})"
        return result

    def getBehInitProtocols(self):
        result = ""
        parametrs = self.getInputParametrs()
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
                f"MAIN_{self.ident_uniq_name_upper}{parametrs} = ("
                + main_protocol
                + "),"
            )
            main_protocol_part = f"MAIN_{self.ident_uniq_name_upper}{parametrs}"
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
            struct_part += element.getName()

        if len(struct_part) > 0:
            struct_flag = True
            if always_flag or main_flag:
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
                f"INIT_{self.ident_uniq_name_upper}{parametrs} = " + init_protocol + ","
            )
            init_protocol_part = f"INIT_{self.ident_uniq_name_upper}{parametrs}"
            if main_flag or always_flag or struct_flag:
                init_protocol_part += " || "
            if main_flag:
                init_protocol += "\n"
            result = init_protocol + result
        b_body = f"{init_protocol_part}{struct_part}{always_part}{main_protocol_part}"
        b0 = ""

        if len(b_body) > 0:
            b0 = f"B_{self.ident_uniq_name_upper}{parametrs} = {{{b_body}}},"
            if main_flag or init_flag:
                b0 += "\n"

        result = b0 + result
        return result

    def __repr__(self):
        return f"\tModule({self.identifier!r}, {self.ident_uniq_name!r}, {self.element_type!r}\n)"


class ModuleArray(BasicArray):
    def __init__(self):
        super().__init__(Module)

    def copy(self):
        new_aray: ModuleArray = ModuleArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def findModuleByUniqIdentifier(self, ident_uniq_name: str):
        for element in self.elements:
            if element.ident_uniq_name == ident_uniq_name:
                return element
        return None

    def getElements(self) -> List[Module]:
        return self.elements

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_ident_uniq_names: List[str] | None = None,
        exclude_ident_uniq_name: str | None = None,
    ):
        result: ModuleArray = ModuleArray()
        elements = self.elements

        if include is None and exclude is None:
            return self

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                include_ident_uniq_names is not None
                and element.ident_uniq_name not in include_ident_uniq_names
            ):
                continue
            if (
                exclude_ident_uniq_name is not None
                and element.ident_uniq_name is exclude_ident_uniq_name
            ):
                continue

            result.addElement(element)

        return result

    def __repr__(self):
        return f"ModulesArray(\n{self.elements!r}\n)"
