from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.module import Module


def genvarDeclaration2Aplan(
    ctx: SystemVerilogParser.Genvar_declarationContext,
    module: Module,
):
    assign_name = ""
    for element in ctx.list_of_genvar_identifiers().genvar_identifier():
        identifier = element.identifier().getText()
        module.declarations.addElement(
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
