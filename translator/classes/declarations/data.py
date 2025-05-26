from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from translator.classes.expressions.expression import ExpressionTranslator
from translator.declarations.struct_declaration import createArrayStruct
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    dataTypeToStr,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


class DataDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        if ctx.data_type_or_implicit() is not None:
            data_type = ctx.data_type_or_implicit().data_type()
            if data_type is not None:
                if data_type.struct_union():
                    struct = self._translator_ptr.translate(
                        "struct_decl",
                        ctx,
                    )
                else:
                    struct = None

                data_type = dataTypeToStr(data_type)
                if len(data_type) > 0:
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
                        data_check_type = DeclTypes.checkType(data_type, types)
                    aplan_vector_size = [0]

                    packed_dimension = (
                        ctx.data_type_or_implicit().data_type().packed_dimension(0)
                    )

                    vector_size = None
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
                    if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                        declaration = (
                            ctx.list_of_variable_decl_assignments().variable_decl_assignment()
                        )

                    for elem in declaration:
                        if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                            original_identifier = (
                                elem.variable_identifier().identifier().getText()
                            )

                        if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                            unpacked_dimention = elem.variable_dimension(0)

                        element_type = ElementsTypes.NONE_ELEMENT

                        dimension_size = 0
                        dimension_size_expression = ""
                        if unpacked_dimention is not None:
                            dimension = unpacked_dimention.getText()
                            dimension_size_expression = dimension

                            dimension = extractDimentionSize(dimension)
                            if dimension == None:
                                dimension = 0

                            dimension_size = replaceValueParametrsCalls(
                                self.module.value_parametrs, str(dimension)
                            )
                            dimension_size = int(dimension_size)
                            if data_check_type == DeclTypes.INT:
                                data_check_type = DeclTypes.ARRAY

                                self._translator_ptr.getTranslator(
                                    "expr"
                                ).createSizeExpression(
                                    original_identifier,
                                    dimension_size,
                                    elem.getSourceInterval(),
                                )

                                size_expression = self._translator_ptr.translate(
                                    "array",
                                    original_identifier,
                                    DeclTypes.INT,
                                    elem.getSourceInterval(),
                                )

                        assign_name = ""
                        new_decl = Declaration(
                            data_check_type,
                            original_identifier,
                            assign_name,
                            size_expression,
                            aplan_vector_size[0],
                            dimension_size_expression,
                            dimension_size,
                            elem.getSourceInterval(),
                            name_space_level=self.getLastNameSpaceLevel(),
                        )

                        decl_unique, decl_index = self.module.declarations.addElement(
                            new_decl
                        )
                        # if (
                        #     name_space != ElementsTypes.NONE_ELEMENT
                        #     or name_space != ElementsTypes.LOOP_ELEMENT
                        #     or name_space != ElementsTypes.GENERATE_ELEMENT
                        #  ):
                        #     self.module.declarations.elements[decl_index] = new_decl

                        if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                            expression = elem.expression()

                        declaration = self.module.declarations.getElementByIndex(
                            decl_index
                        )

                        if expression is not None:
                            expression = expression.getText()
                            stmt: Structure | None = (
                                self.structure_pointer_list.getLastElement()
                            )
                            if stmt is not None:
                                stmt.elements.addElement(declaration)
                                beh_index = stmt.getLastBehaviorIndex()
                                (
                                    action_pointer,
                                    assign_name,
                                    source_interval,
                                    uniq_action,
                                ) = self._translator_ptr.translate(
                                    "expr",
                                    elem,
                                    ElementsTypes.ASSIGN_ELEMENT,
                                    sv_structure=stmt,
                                )
                                if beh_index is not None and assign_name is not None:
                                    stmt.behavior[beh_index].addBody(
                                        BodyElement(
                                            assign_name,
                                            action_pointer,
                                            ElementsTypes.ACTION_ELEMENT,
                                        )
                                    )
                            else:
                                if decl_unique:
                                    (
                                        action_pointer,
                                        assign_name,
                                        source_interval,
                                        uniq_action,
                                    ) = self._translator_ptr.translate(
                                        "expr",
                                        elem,
                                        ElementsTypes.ASSIGN_ELEMENT,
                                        sv_structure=stmt,
                                    )
                                    declaration.expression = assign_name
                                    declaration.action = action_pointer

        else:

            self._translator_ptr.translate("typedef", ctx)
