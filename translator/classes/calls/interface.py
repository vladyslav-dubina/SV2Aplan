import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.design_unit_call import DesignUnitCall
from AppModule.app.classes.parametrs import Parametr
from translator.classes.base_translator import BaseTranslator
from translator.translation_mngr import TranslationManager


class InterfaceCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
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

        design_unit_call = DesignUnitCall(
            destination_identifier,
            object_name,
            self.design_unit.identifier,
            destination_identifier,
            None,
            None,
        )

        try:
            previous_file_path = self._program.file_path
            file_path = self.file_mngrreplace_filename(
                self._program.file_path, f"{destination_identifier}.sv"
            )
            translation_mngr = TranslationManager()
            translation_mngr.setup(file_path)
            translation_mngr.translate(design_unit_call)
        except Exception as e:
            self._program.design_units_calls.addElement(design_unit_call)

        self._program.file_path = previous_file_path

        self.design_unit.input_parametrs.addElement(Parametr(object_name, "var"))
