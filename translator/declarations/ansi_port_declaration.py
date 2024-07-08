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
        assign_name, source_interval, uniq_action = self.expression2Aplan(
            expression, ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        declaration = self.module.declarations.getElementByIndex(decl_index)
        declaration.expression = assign_name