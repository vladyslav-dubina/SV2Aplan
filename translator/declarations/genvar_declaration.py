from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.module import Module
from translator.system_verilog_to_aplan import SV2aplan


def genvarDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Genvar_declarationContext,
):
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
