import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.design_unit import DesignUnit
from translator.classes.base_translator import BaseTranslator


class ModuleDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Module_declarationContext) -> None:
        if ctx.module_ansi_header() is not None:
            identifier = ctx.module_ansi_header().module_identifier().getText()
        elif ctx.module_nonansi_header() is not None:
            identifier = ctx.module_nonansi_header().module_identifier().getText()
        else:
            raise (ValueError("DesignUnit type unhandled"))

        (identifier, uniq_name) = self._translator_ptr.getTranslator(
            "design_unit_call"
        ).resolve(identifier)
        index = self.design_units.addElement(
            DesignUnit(identifier, ctx.getSourceInterval(), uniq_name)
        )
        self.design_unit = self.design_units.getElementByIndex(index)
