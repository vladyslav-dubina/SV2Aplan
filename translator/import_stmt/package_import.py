from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr, ActionParametrArray
from classes.action_precondition import ActionPrecondition, ActionPreconditionArray
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import Declaration
from classes.element_types import ElementsTypes
from classes.module_call import ModuleCall
from classes.value_parametrs import ValueParametr
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from classes.tasks import Task
from program.program import Program
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replace_filename
from utils.utils import Color, Counters_Object, printWithColor


def packageImport2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Package_import_declarationContext,
):
    from translator.translator import SystemVerilogFinder

    for element in ctx.package_import_item():
        package_identifier = element.package_identifier()
        package_identifier = package_identifier.getText()
        if package_identifier is not None:
            package_program = self.program.modules.getElement(package_identifier)
            if package_program is None:
                previous_file_path = self.program.file_path
                file_path = replace_filename(
                    self.program.file_path, f"{package_identifier}.sv"
                )
                file_data = self.program.readFileData(file_path)
                finder = SystemVerilogFinder()
                finder.setUp(file_data)
                finder.startTranslate(self.program)

                self.program.file_path = previous_file_path

            package = self.program.modules.findModuleByUniqIdentifier(
                package_identifier
            )
            if package is not None:
                identifier = element.identifier()

                if identifier is not None:
                    identifier = identifier.getText()
                    result = package.findElementByIdentifier(identifier)
                    for module_element in result:
                        if isinstance(module_element, Declaration):
                            self.module.declarations.addElement(module_element)
                        elif isinstance(module_element, Action):
                            self.module.actions.addElement(module_element)
                        elif isinstance(module_element, Structure):
                            self.module.structures.addElement(module_element)
                        elif isinstance(module_element, Task):
                            self.module.tasks.addElement(module_element)
                        elif isinstance(module_element, Protocol):
                            self.module.out_of_block_elements.addElement(module_element)
                        elif isinstance(module_element, ValueParametr):
                            self.module.value_parametrs.addElement(module_element)

                    self.program.modules.removeElement(
                        package
                    )  # remove after take all needed elements
                else:
                    if len(package.getBehInitProtocols()) > 0:
                        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                        call_b = "PACKAGE_IMPORT_B_{}".format(
                            Counters_Object.getCounter(CounterTypes.B_COUNTER)
                        )
                        struct_call = Protocol(
                            call_b,
                            ctx.getSourceInterval(),
                            ElementsTypes.MODULE_CALL_ELEMENT,
                        )
                        struct_call.addBody(
                            BodyElement(
                                identifier=f"B_{package_identifier.upper()}",
                                element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            )
                        )
                        self.module.out_of_block_elements.addElement(struct_call)

                    self.module.packages_and_objects.addElement(package)
