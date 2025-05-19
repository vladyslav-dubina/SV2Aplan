from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module_call import ModuleCall
from classes.parametrs import Parametr
from translator.classes.base_translator import BaseTranslator
from translator.translation_mngr import TranslationManager
from utils.string_formating import replace_filename


class InterfaceCallTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Ansi_port_declarationContext) -> None:
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

        self._program.file_path = previous_file_path

        self.module.input_parametrs.addElement(Parametr(object_name, "var"))
