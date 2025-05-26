import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module import Module
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
            raise (ValueError("Module type unhandled"))

        (identifier, uniq_name) = self._translator_ptr.getTranslator(
            "module_call"
        ).resolve(identifier)
        index = self.modules.addElement(
            Module(identifier, ctx.getSourceInterval(), uniq_name)
        )
        self.module = self.modules.getElementByIndex(index)
