from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.module import Module
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import (
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def netDeclaration2Aplan(
    ctx: SystemVerilogParser.Net_declarationContext,
    module: Module,
):
    data_type = ctx.data_type_or_implicit()

    unpacked_dimention = ctx.unpacked_dimension(0)
    dimension_size = 0
    dimension_size_expression = ""
    if unpacked_dimention is not None:
        dimension = unpacked_dimention.getText()
        dimension_size_expression = dimension
        dimension = replaceParametrsCalls(module.parametrs, dimension)
        dimension_size = extractDimentionSize(dimension)

    aplan_vector_size = [0]
    size_expression = ""
    if data_type:
        size_expression = data_type.getText()
        data_type = replaceParametrsCalls(module.parametrs, data_type.getText())
        vector_size = extractVectorSize(data_type)
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

    if ctx.net_type().getText() == "wire":
        for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
            identifier = elem.net_identifier().identifier().getText()
            assign_name = ""
            decl_unique, decl_index = module.declarations.addElement(
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
                    sv2aplan = SV2aplan(module)
                    assign_name, source_interval = sv2aplan.expression2Aplan(
                        elem.getText(),
                        ElementsTypes.ASSIGN_ELEMENT,
                        elem.getSourceInterval(),
                    )
                    declaration = module.declarations.getElementByIndex(decl_index)
                    declaration.expression = assign_name
