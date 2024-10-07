from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.typedef import Typedef
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    Color,
    Counters_Object,
    dataTypeToStr,
    extractDimentionSize,
    extractVectorSize,
    printWithColor,
    vectorSize2AplanVectorSize,
)


def structDeclaration2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Data_declarationContext
):
    struct_decl = ctx.data_type_or_implicit().data_type()
    unique_identifier = "{0}_{1}".format(
        "struct",
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
    )
    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    typedef = Typedef(
        unique_identifier,
        unique_identifier,
        struct_decl.getSourceInterval(),
        self.program.file_path,
        DeclTypes.STRUCT_TYPE,
    )

    structMembersToDeclarations(self, struct_decl, typedef)

    if self.module:
        decl_unique, decl_index = self.module.typedefs.addElement(typedef)
    else:
        decl_unique, decl_index = self.program.typedefs.addElement(typedef)

    return typedef


def structMembersToDeclarations(
    self: SV2aplan, ctx: SystemVerilogParser.Data_typeContext, typedef: Typedef
):
    for element in ctx.struct_union_member():
        if isinstance(element, SystemVerilogParser.Struct_union_memberContext):
            lsit_var_decl_assignment: (
                SystemVerilogParser.List_of_variable_decl_assignmentsContext
            ) = element.list_of_variable_decl_assignments()
            for (
                var_decl_assignment
            ) in lsit_var_decl_assignment.variable_decl_assignment():
                if isinstance(
                    var_decl_assignment,
                    SystemVerilogParser.Variable_decl_assignmentContext,
                ):
                    var_name = var_decl_assignment.variable_identifier().getText()
                    data_type = element.data_type_or_void().data_type()
                    packed_dimension = data_type.packed_dimension(0)
                    data_type_str = dataTypeToStr(data_type)
                    if len(data_type_str) > 0:
                        if self.module:
                            types = self.module.typedefs.getElementsIE().getElements()
                            packages = self.module.packages_and_objects.getElementsIE(
                                include=ElementsTypes.PACKAGE_ELEMENT
                            )
                            packages += self.module.packages_and_objects.getElementsIE(
                                include=ElementsTypes.OBJECT_ELEMENT
                            )
                            for package in packages.getElements():
                                types += package.typedefs.getElementsIE().getElements()
                        else:
                            types = []

                        data_check_type = DeclTypes.checkType(data_type_str, types)
                        size_expression = ""
                        vector_size = None
                        aplan_vector_size = [0]
                        if packed_dimension is not None:
                            vector_size = packed_dimension.getText()
                            size_expression = vector_size
                            if self.module:
                                vector_size = replaceValueParametrsCalls(
                                    self.module.value_parametrs, vector_size
                                )
                            vector_size = extractVectorSize(vector_size)

                        unpacked_dimention = var_decl_assignment.variable_dimension(0)

                        dimension_size = 0
                        dimension_size_expression = ""
                        if unpacked_dimention is not None:
                            dimension = unpacked_dimention.getText()
                            dimension_size_expression = dimension
                            dimension = replaceValueParametrsCalls(
                                self.module.value_parametrs, dimension
                            )
                            dimension_size = extractDimentionSize(dimension)

                        if (
                            data_check_type == DeclTypes.ENUM
                            or data_check_type == DeclTypes.STRUCT
                        ):
                            for type in types:
                                if isinstance(type, Typedef):
                                    if type.identifier in data_type_str:
                                        size_expression = type.unique_identifier

                        if vector_size is not None:
                            aplan_vector_size = vectorSize2AplanVectorSize(
                                vector_size[0], vector_size[1]
                            )

                        new_decl = Declaration(
                            data_check_type,
                            var_name,
                            "",
                            size_expression,
                            aplan_vector_size[0],
                            dimension_size_expression,
                            dimension_size,
                            element.getSourceInterval(),
                        )
                        typedef.declarations.addElement(new_decl)
                else:
                    printWithColor(
                        f"WARNING: Struct or union member decl assignment is not SystemVerilogParser.Variable_decl_assignmentContext \n",
                        Color.YELLOW,
                    )
                    raise Warning(
                        f"WARNING: Struct or union member decl assignment is not SystemVerilogParser.Variable_decl_assignmentContext \n"
                    )
        else:
            printWithColor(
                f"WARNING: Struct or union member is not SystemVerilogParser.Struct_union_memberContext \n",
                Color.YELLOW,
            )
            raise Warning(
                f"WARNING: Struct or union member is not SystemVerilogParser.Struct_union_memberContext \n"
            )


def typedefDecaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Data_declarationContext,
):
    type_declaration: SystemVerilogParser.Type_declarationContext | None = (
        ctx.type_declaration()
    )
    if type_declaration is not None:
        data_type: SystemVerilogParser.Data_typeContext | None = (
            type_declaration.data_type()
        )
        if data_type.ENUM() or data_type.struct_union():
            for type_identifier in type_declaration.type_identifier():
                enum_type_identifier = "{0}".format(type_identifier.getText())
                unique_identifier = "{0}_{1}".format(
                    enum_type_identifier,
                    Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
                )
                Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
                decl_type = DeclTypes.ENUM_TYPE

                if data_type.struct_union():
                    decl_type = DeclTypes.STRUCT_TYPE

                typedef = Typedef(
                    enum_type_identifier,
                    unique_identifier,
                    type_identifier.getSourceInterval(),
                    self.program.file_path,
                    decl_type,
                )

                if data_type.ENUM():
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
                elif data_type.struct_union():
                    structMembersToDeclarations(self, data_type, typedef)

                if self.module:
                    decl_unique, decl_index = self.module.typedefs.addElement(typedef)
                else:
                    decl_unique, decl_index = self.program.typedefs.addElement(typedef)


def createArrayStruct(
    self: SV2aplan,
    identifier: str,
    decl_type: DeclTypes,
    source_interval: Tuple[int, int],
):
    enum_type_identifier = "{0}".format(identifier)
    unique_identifier = "{0}_{1}".format(
        enum_type_identifier,
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
    )
    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    typedef = Typedef(
        enum_type_identifier,
        unique_identifier,
        source_interval,
        self.program.file_path,
        DeclTypes.STRUCT_TYPE,
    )

    new_decl = Declaration(
        DeclTypes.INT,
        "size",
        "",
        "",
        0,
        "",
        0,
        (0, 0),
    )
    typedef.declarations.addElement(new_decl)

    new_decl = Declaration(
        decl_type,
        "value",
        "",
        "",
        0,
        "",
        1,
        (0, 1),
    )
    typedef.declarations.addElement(new_decl)

    if self.module:
        decl_unique, decl_index = self.module.typedefs.addElement(typedef)
    else:
        decl_unique, decl_index = self.program.typedefs.addElement(typedef)

    return unique_identifier
