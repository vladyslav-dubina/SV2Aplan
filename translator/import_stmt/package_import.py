from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr, ActionParametrArray
from classes.action_precondition import ActionPrecondition, ActionPreconditionArray
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module_call import ModuleCall
from classes.protocols import Protocol
from program.program import Program
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replace_filename
from utils.utils import Color, Counters_Object, printWithColor


def packageImport2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Package_import_declarationContext,
    program: Program,
):
    from translator.translator import SystemVerilogFinder

    for element in ctx.package_import_item():
        package_identifier = element.package_identifier()
        package_identifier = package_identifier.getText()
        if package_identifier is not None:
            try:
                previous_file_path = program.file_path
                file_path = replace_filename(
                    program.file_path, f"{package_identifier}.sv"
                )
                file_data = program.readFileData(file_path)
                finder = SystemVerilogFinder()
                finder.setUp(file_data)
                finder.startTranslate(program)
                
            finally:
                program.file_path = previous_file_path
                package = program.modules.findModuleByUniqIdentifier(package_identifier)
                self.packages = program.modules.getPackeges()
                if package is not None:
                    identifier = element.identifier()

                    if identifier is not None:
                        package.findElementByIdentifier(element.identifier)
                        program.modules.removeElement(
                            package
                        )  # remove after take all needed elements
                    else:
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
                            (
                                f"B_{package_identifier.upper()}",
                                ElementsTypes.PROTOCOL_ELEMENT,
                            )
                        )
                        self.module.out_of_block_elements.addElement(struct_call)
