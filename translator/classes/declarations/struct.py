from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator
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


class StructDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> Typedef:
        struct_decl = ctx.data_type_or_implicit().data_type()
        unique_identifier = "{0}_{1}".format(
            "struct",
            self.getLastNameSpaceLevel(),
        )
        typedef = Typedef(
            unique_identifier,
            unique_identifier,
            struct_decl.getSourceInterval(),
            self._program.file_path,
            DeclTypes.STRUCT_TYPE,
        )

        self.structMembersToDeclarations(struct_decl, typedef)

        if self.module:
            decl_unique, decl_index = self.module.typedefs.addElement(typedef)
        else:
            decl_unique, decl_index = self._program.typedefs.addElement(typedef)

        return typedef

    def structMembersToDeclarations(
        self, ctx: SystemVerilogParser.Data_typeContext, typedef: Typedef
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
                                types = (
                                    self.module.typedefs.getElementsIE().getElements()
                                )
                                packages = (
                                    self.module.packages_and_objects.getElementsIE(
                                        include=ElementsTypes.PACKAGE_ELEMENT
                                    )
                                )
                                packages += (
                                    self.module.packages_and_objects.getElementsIE(
                                        include=ElementsTypes.OBJECT_ELEMENT
                                    )
                                )
                                for package in packages.getElements():
                                    types += (
                                        package.typedefs.getElementsIE().getElements()
                                    )
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

                            unpacked_dimention = var_decl_assignment.variable_dimension(
                                0
                            )

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