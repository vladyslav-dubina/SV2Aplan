from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.module import Module
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import (
    Counters_Object,
    CounterTypes,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def dataDecaration2Aplan(
    ctx: SystemVerilogParser.Data_declarationContext,
    module: Module,
    listener: bool,
    name_space: ElementsTypes = ElementsTypes.NONE_ELEMENT,
):
    data_type = ctx.data_type_or_implicit().getText()
    if len(data_type) > 0:
        data_check_type = DeclTypes.checkType(data_type)
        aplan_vector_size = [0]
        size_expression = data_type
        data_type = replaceParametrsCalls(module.parametrs, data_type)
        vector_size = extractVectorSize(data_type)
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        for elem in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
            identifier = elem.variable_identifier().identifier().getText()
            unique_identifier = identifier
            counter = Counters_Object.selectCounter(name_space)
            if name_space != ElementsTypes.NONE_ELEMENT and counter is not CounterTypes.NONE_COUNTER:
                unique_identifier += f"_{Counters_Object.getCounter(counter)}"
            unpacked_dimention = elem.variable_dimension(0)
            dimension_size = 0
            dimension_size_expression = ""
            if unpacked_dimention is not None:
                dimension = unpacked_dimention.getText()
                dimension_size_expression = dimension
                dimension = replaceParametrsCalls(module.parametrs, dimension)
                dimension_size = extractDimentionSize(dimension)

            assign_name = ""
            decl_unique, decl_index = module.declarations.addElement(
                Declaration(
                    data_check_type,
                    identifier,
                    unique_identifier,
                    assign_name,
                    size_expression,
                    aplan_vector_size[0],
                    dimension_size_expression,
                    dimension_size,
                    ctx.getSourceInterval(),
                )
            )

            if elem.expression() is not None:
                expression = elem.expression().getText()
                sv2aplan = SV2aplan(module)
                assign_name = sv2aplan.declaration2Aplan(elem)
                if listener == False:
                    return assign_name
                else:
                    if decl_unique:
                        declaration = module.declarations.getElementByIndex(decl_index)
                        declaration.expression = assign_name
