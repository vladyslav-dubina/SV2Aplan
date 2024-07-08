from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import (
    Counters_Object,
    CounterTypes,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def dataDecaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Data_declarationContext,
    listener: bool,
    sv_structure: Structure | None = None,
    name_space: ElementsTypes = ElementsTypes.NONE_ELEMENT,
):
    data_type = ctx.data_type_or_implicit().getText()
    if len(data_type) > 0:
        data_check_type = DeclTypes.checkType(data_type)
        aplan_vector_size = [0]
        size_expression = data_type
        data_type = replaceParametrsCalls(self.module.parametrs, data_type)
        vector_size = extractVectorSize(data_type)
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        for elem in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
            original_identifier = elem.variable_identifier().identifier().getText()
            identifier = original_identifier
            if name_space != ElementsTypes.NONE_ELEMENT:
                identifier += (
                    f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
                )
                Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
            unpacked_dimention = elem.variable_dimension(0)
            dimension_size = 0
            dimension_size_expression = ""
            if unpacked_dimention is not None:
                dimension = unpacked_dimention.getText()
                dimension_size_expression = dimension
                dimension = replaceParametrsCalls(self.module.parametrs, dimension)
                dimension_size = extractDimentionSize(dimension)

            assign_name = ""
            decl_unique, decl_index = self.module.declarations.addElement(
                Declaration(
                    data_check_type,
                    identifier,
                    assign_name,
                    size_expression,
                    aplan_vector_size[0],
                    dimension_size_expression,
                    dimension_size,
                    elem.getSourceInterval(),
                )
            )

            if listener == False:
                self.module.name_change.addElement(
                    NameChange(identifier, ctx.getSourceInterval(), original_identifier)
                )

            if elem.expression() is not None:
                expression = elem.expression().getText()
                if listener == False:
                    if sv_structure is not None:
                        beh_index = sv_structure.getLastBehaviorIndex()
                        (
                            assign_name,
                            source_interval,
                            uniq_action,
                        ) = self.expression2Aplan(
                            elem.getText(),
                            ElementsTypes.ASSIGN_ELEMENT,
                            elem.getSourceInterval(),
                        )
                        if beh_index is not None and assign_name is not None:
                            sv_structure.behavior[beh_index].addBody(
                                (assign_name, ElementsTypes.ACTION_ELEMENT)
                            )
                else:
                    if decl_unique:
                        (
                            assign_name,
                            source_interval,
                            uniq_action,
                        ) = self.expression2Aplan(
                            elem.getText(),
                            ElementsTypes.ASSIGN_ELEMENT,
                            elem.getSourceInterval(),
                        )
                        declaration = self.module.declarations.getElementByIndex(
                            decl_index
                        )
                        declaration.expression = assign_name

        return identifier
