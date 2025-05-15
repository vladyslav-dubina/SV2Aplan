from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from translator.classes.base_translator import BaseTranslator


class GenvarDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Genvar_declarationContext) -> None:
        assign_name = ""
        for element in ctx.list_of_genvar_identifiers().genvar_identifier():
            identifier = element.identifier().getText()
            self.module.declarations.addElement(
                Declaration(
                    DeclTypes.INT,
                    identifier,
                    assign_name,
                    "",
                    0,
                    "",
                    0,
                    element.getSourceInterval(),
                )
            )
