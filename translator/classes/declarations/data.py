import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclType, DeclTypes
from AppModule.app.classes.element_types import ElementsTypes
from translator.classes.base_translator import BaseTranslator


class DataDeclTranslator(BaseTranslator):
    need_delete_type = False
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        data_type_or_implicit: SystemVerilogParser.Data_type_or_implicitContext = (
            ctx.data_type_or_implicit()
        )
        if not data_type_or_implicit:
            self._translator_ptr.translate("typedef", ctx)
            return

        data_type: SystemVerilogParser.Data_typeContext = (
            data_type_or_implicit.data_type()
        )
        if not data_type:
            return

        struct = None
        struct_union: SystemVerilogParser.Struct_unionContext = data_type.struct_union()
        if struct_union:
            struct = self._translator_ptr.translate(
                "struct_decl",
                struct_union,
            )

        data_type_str = self._translator_ptr.getTranslator("data_decl").dataTypeToStr(
            data_type
        )
        if len(data_type_str) <= 0:
            return

        size_expression = ""
        if struct:
            data_check_type = DeclTypes.STRUCT
            size_expression = struct.unique_identifier
        else:
            if self.design_unit:
                types = self.design_unit.typedefs.getElementsIE().getElements()
                packages = self.design_unit.packages_and_objects.getElementsIE(
                    include=ElementsTypes.PACKAGE_ELEMENT
                )
                packages += self.design_unit.packages_and_objects.getElementsIE(
                    include=ElementsTypes.OBJECT_ELEMENT
                )
                for package in packages.getElements():
                    types += package.typedefs.getElementsIE().getElements()

            else:
                types = []

            data_check_type = DeclTypes.checkType(data_type_str, types)

        packed_dimension = data_type.packed_dimension(0)
        vector_size = None
        if packed_dimension is not None:
            vector_size = packed_dimension.getText()
            size_expression = vector_size
            vector_size = self.str_formater.replaceValueParametrsCalls(
                self.design_unit.value_parametrs, vector_size
            )
            vector_size = self.utils.extractVectorSize(vector_size)

        aplan_vector_size = [0]
        if vector_size is not None:
            aplan_vector_size = self.utils.vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        self.decl_type_array.addElement(
            DeclType(
                data_check_type,
                size_expression,
                aplan_vector_size,
                self.getLastNameSpaceLevel(),
            )
        )
        self.need_delete_type = True

    def exit(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        if self.need_delete_type:
            self.decl_type_array.removeLastElement()
            self.need_delete_type = False

        data_type_or_implicit: SystemVerilogParser.Data_type_or_implicitContext = (
            ctx.data_type_or_implicit()
        )
        if not data_type_or_implicit:
            self._translator_ptr.exit("typedef", ctx)
            return

    def dataTypeToStr(
        self,
        ctx,
    ):
        result = None
        if ctx.integer_vector_type() is not None:
            result = ctx.integer_vector_type().getText()
        elif ctx.signing() is not None:
            result = ctx.signing().getText()
        elif ctx.integer_atom_type() is not None:
            result = ctx.integer_atom_type().getText()
        elif ctx.non_integer_type() is not None:
            result = ctx.non_integer_type().getText()
        elif ctx.struct_union() is not None:
            result = ctx.struct_union().getText()
        elif ctx.interface_identifier() is not None:
            result = ctx.interface_identifier().getText()
        elif ctx.parameter_value_assignment() is not None:
            result = ctx.parameter_value_assignment().getText()
        elif ctx.modport_identifier() is not None:
            result = ctx.modport_identifier().getText()
        elif ctx.type_identifier() is not None:
            result = ctx.type_identifier().getText()
        elif ctx.type_identifier() is not None:
            result = ctx.type_identifier().getText()
        return result
