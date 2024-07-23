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


def ansiPortDeclaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Ansi_port_declarationContext,
):
    """The function `ansiPortDeclaration2AplanImpl` processes ANSI port declarations in SystemVerilog and adds them
    to a module's declarations in Aplan format.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter in Python is a reference to the current instance of the class. In this
    context, it is used within a method of the `SV2aplan` class to refer to the current instance of that
    class. It allows you to access the attributes and methods of the class within
    ctx : SystemVerilogParser.Ansi_port_declarationContext
        The `ctx` parameter in the `ansiPortDeclaration2AplanImpl` function is of type
    `SystemVerilogParser.Ansi_port_declarationContext`. It represents the context of an ANSI port
    declaration in SystemVerilog code. This context provides access to various elements and properties
    of the ANSI port

    """
    header = ctx.net_port_header().getText()
    unpacked_dimention = ctx.unpacked_dimension(0)
    dimension_size = 0
    dimension_size_expression = ""
    if unpacked_dimention is not None:
        dimension = unpacked_dimention.getText()
        dimension_size_expression = dimension
        dimension = replaceParametrsCalls(self.module.parametrs, dimension)
        dimension_size = extractDimentionSize(dimension)

    data_type = DeclTypes.INPORT
    index = header.find("output")
    if index != -1:
        data_type = DeclTypes.OUTPORT

    index = header.find("input")
    if index != -1:
        data_type = DeclTypes.INPORT

    size_expression = header
    header = replaceParametrsCalls(self.module.parametrs, header)
    vector_size = extractVectorSize(header)
    aplan_vector_size = [0]

    if vector_size is not None:
        aplan_vector_size = vectorSize2AplanVectorSize(vector_size[0], vector_size[1])

    assign_name = ""
    identifier = ctx.port_identifier().getText()
    port = Declaration(
        data_type,
        identifier,
        assign_name,
        size_expression,
        aplan_vector_size[0],
        dimension_size_expression,
        dimension_size,
        ctx.getSourceInterval(),
    )
    decl_unique, decl_index = self.module.declarations.addElement(port)

    constant_expression = ctx.constant_expression()
    if constant_expression is not None:
        expression = constant_expression.getText()
        action_pointer, assign_name, source_interval, uniq_action = (
            self.expression2Aplan(
                expression, ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
            )
        )
        declaration = self.module.declarations.getElementByIndex(decl_index)
        declaration.expression = assign_name
        declaration.action = action_pointer
