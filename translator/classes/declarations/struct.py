from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclType, DeclTypes, Declaration
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


class StructUnionMemberContextTranlator(BaseTranslator):
    need_delete_type = False

    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Struct_union_memberContext) -> Typedef:
        data_type_or_void: SystemVerilogParser.Data_type_or_voidContext = (
            ctx.data_type_or_void()
        )
        if not data_type_or_void:
            return

        data_type: SystemVerilogParser.Data_typeContext = data_type_or_void.data_type()

        if not data_type:
            return

        data_type_str = dataTypeToStr(data_type)
        if len(data_type_str) <= 0:
            return

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
        packed_dimension = data_type.packed_dimension(0)
        vector_size = None
        if packed_dimension is not None:
            vector_size = packed_dimension.getText()
            size_expression = vector_size
            vector_size = replaceValueParametrsCalls(
                self.module.value_parametrs, vector_size
            )
            vector_size = extractVectorSize(vector_size)

        aplan_vector_size = [0]
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        self.decl_type_array.addElement(
            DeclType(
                data_check_type,
                size_expression,
                aplan_vector_size,
                self.getLastNameSpaceLevel(),
                inside_the_struct=True,
            )
        )
        self.need_delete_type = True

    def exit(self, ctx: SystemVerilogParser.Struct_union_memberContext):
        if self.need_delete_type:
            self.decl_type_array.removeLastElement()
            self.need_delete_type = False


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

        # self.structMembersToDeclarations(struct_decl, typedef)

        self.addTypedef(typedef)

        return typedef