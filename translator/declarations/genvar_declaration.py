from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from translator.translator import Translator


def genvarDeclaration2AplanImpl(
    self: Translator,
    ctx: SystemVerilogParser.Genvar_declarationContext,
):
    """The function `genvarDeclaration2AplanImpl` processes SystemVerilog genvar declarations and adds them
    to a module's declarations in Aplan format.

    Parameters
    ----------
    self : Translator
        The `self` parameter in the `genvarDeclaration2AplanImpl` function refers to the instance of the
    `Translator` class to which the method belongs. It is a common convention in Python to use `self` as
    the first parameter in instance methods to refer to the instance
    ctx : SystemVerilogParser.Genvar_declarationContext
        The `ctx` parameter in the `genvarDeclaration2AplanImpl` function represents the context of the
    `Genvar_declaration` in the SystemVerilog code. It is of type
    `SystemVerilogParser.Genvar_declarationContext` and contains information about the genvar
    declaration in the parse tree

    """
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
