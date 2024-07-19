from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import (
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def netDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Net_declarationContext,
):
    """The function `netDeclaration2AplanImpl` processes SystemVerilog net declarations and adds them
    to a module's declarations in Aplan format.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter in the `netDeclaration2AplanImpl` function refers to the instance of the
    `SV2aplan` class to which the method belongs. It is a common convention in Python to use `self` as
    the first parameter in instance methods to refer to the instance itself
    ctx : SystemVerilogParser.Net_declarationContext
        The `ctx` parameter in the `netDeclaration2AplanImpl` function is of type
    `SystemVerilogParser.Net_declarationContext`. This parameter represents the context of a net
    declaration in a SystemVerilog code snippet. It contains information about the data type,
    dimensions, and assignments associated with the

    """
    data_type = ctx.data_type_or_implicit()

    unpacked_dimention = ctx.unpacked_dimension(0)
    dimension_size = 0
    dimension_size_expression = ""
    if unpacked_dimention is not None:
        dimension = unpacked_dimention.getText()
        dimension_size_expression = dimension
        dimension = replaceParametrsCalls(self.module.parametrs, dimension)
        dimension_size = extractDimentionSize(dimension)

    aplan_vector_size = [0]
    size_expression = ""
    if data_type:
        size_expression = data_type.getText()
        data_type = replaceParametrsCalls(self.module.parametrs, data_type.getText())
        vector_size = extractVectorSize(data_type)
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

    if ctx.net_type().getText() == "wire":
        for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
            identifier = elem.net_identifier().identifier().getText()
            assign_name = ""
            decl_unique, decl_index = self.module.declarations.addElement(
                Declaration(
                    DeclTypes.WIRE,
                    identifier,
                    assign_name,
                    size_expression,
                    aplan_vector_size[0],
                    dimension_size_expression,
                    dimension_size,
                    elem.getSourceInterval(),
                )
            )

            if elem.expression():
                expression = elem.expression().getText()
                if expression:
                    assign_name, source_interval, uniq_action = self.expression2Aplan(
                        elem.getText(),
                        ElementsTypes.ASSIGN_ELEMENT,
                        elem.getSourceInterval(),
                    )
                    declaration = self.module.declarations.getElementByIndex(decl_index)
                    declaration.expression = assign_name
