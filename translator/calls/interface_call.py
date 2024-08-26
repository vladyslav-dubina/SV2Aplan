from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module_call import ModuleCall
from classes.parametrs import Parametr
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replace_filename


def interfaceCall2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Ansi_port_declarationContext,
):
    from translator.translator import SystemVerilogFinder

    destination_identifier = (
        ctx.net_port_header()
        .net_port_type()
        .data_type_or_implicit()
        .data_type()
        .getText()
    )

    object_name = ctx.port_identifier().identifier().getText()

    module_call = ModuleCall(
        destination_identifier,
        object_name,
        self.module.identifier,
        destination_identifier,
        None,
        None,
    )

    try:
        previous_file_path = self.program.file_path
        file_path = replace_filename(
            self.program.file_path, f"{destination_identifier}.sv"
        )
        file_data = self.program.readFileData(file_path)
        finder = SystemVerilogFinder()
        finder.setUp(file_data)
        finder.startTranslate(self.program, module_call)
    except Exception as e:

        self.program.module_calls.addElement(module_call)

    self.program.file_path = previous_file_path

    self.module.input_parametrs.addElement(Parametr(object_name, "var"))
