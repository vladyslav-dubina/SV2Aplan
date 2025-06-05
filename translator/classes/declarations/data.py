import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclType, DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    Counters_Object,
    dataTypeToStr,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


class DataDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        if ctx.data_type_or_implicit() is None:
            self._translator_ptr.translate("typedef", ctx)
            return
        data_type_or_implicit: SystemVerilogParser.Data_type_or_implicitContext = (
            ctx.data_type_or_implicit()
        )
        data_type: SystemVerilogParser.Data_typeContext = (
            data_type_or_implicit.data_type()
        )
        if not data_type:
            return

        struct = None

        if data_type.struct_union():
            struct = self._translator_ptr.translate(
                "struct_decl",
                ctx,
            )

        data_type_str = dataTypeToStr(data_type)
        if len(data_type_str) <= 0:
            return

        size_expression = ""
        if struct:
            data_check_type = DeclTypes.STRUCT
            size_expression = struct.unique_identifier
        else:
            types = self.module.typedefs.getElementsIE().getElements()
            packages = self.module.packages_and_objects.getElementsIE(
                include=ElementsTypes.PACKAGE_ELEMENT
            )
            packages += self.module.packages_and_objects.getElementsIE(
                include=ElementsTypes.OBJECT_ELEMENT
            )
            for package in packages.getElements():
                types += package.typedefs.getElementsIE().getElements()
            data_check_type = DeclTypes.checkType(data_type_str, types)

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
        if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
            list_of_variable_decl_assignments: (
                SystemVerilogParser.List_of_variable_decl_assignmentsContext
            ) = ctx.list_of_variable_decl_assignments()
            declaration: SystemVerilogParser.Variable_decl_assignmentContext = (
                list_of_variable_decl_assignments.variable_decl_assignment()
            )

        self.decl_type = DeclType(
            data_check_type,
            size_expression,
            aplan_vector_size,
            self.getLastNameSpaceLevel(),
        )