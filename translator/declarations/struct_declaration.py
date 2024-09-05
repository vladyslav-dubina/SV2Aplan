from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.typedef import Typedef
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    Counters_Object,
    dataTypeToStr,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def enumDecaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Data_declarationContext,
):

    type_declaration = ctx.type_declaration()
    if type_declaration is not None:
        data_type = type_declaration.data_type()
        if data_type.ENUM():
            for type_identifier in type_declaration.type_identifier():
                enum_type_identifier = "{0}".format(type_identifier.getText())
                unique_identifier = "{0}_{1}".format(
                    enum_type_identifier,
                    Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
                )
                
                typedef = Typedef(
                    enum_type_identifier,
                    unique_identifier,
                    type_identifier.getSourceInterval(),
                    self.program.file_path,
                    DeclTypes.ENUM_TYPE,
                )
                for index, enum_name_decl in enumerate(
                    data_type.enum_name_declaration()
                ):
                    identifier = enum_name_decl.enum_identifier().getText()
                    new_decl = Declaration(
                        DeclTypes.ENUM,
                        identifier,
                        "",
                        "",
                        0,
                        "",
                        0,
                        enum_name_decl.getSourceInterval(),
                    )
                    typedef.declarations.addElement(new_decl)

                
                if self.module:
                    decl_unique, decl_index = self.module.typedefs.addElement(typedef)
                else:
                    decl_unique, decl_index = self.program.typedefs.addElement(typedef)


def structDeclaration2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Data_declarationContext
):
    struct_decl = ctx.data_type_or_implicit().data_type()
    for element in struct_decl.struct_union_member():

        var_name = element.list_of_variable_decl_assignments().getText()
        data_type = element.data_type_or_void().data_type()
        packed_dimension = data_type.packed_dimension(0)
        data_type_str = dataTypeToStr(data_type)
        size_expression = ""
        vector_size = None
        aplan_vector_size = [0]
        if packed_dimension is not None:
            vector_size = packed_dimension.getText()
            size_expression = vector_size
            vector_size = replaceValueParametrsCalls(
                self.module.value_parametrs, vector_size
            )
            vector_size = extractVectorSize(vector_size)

        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        print(data_type_str, var_name, aplan_vector_size[0])
