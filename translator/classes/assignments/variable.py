import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclType, DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    extractDimentionSize,
)


class VariableDeclTranslator(BaseTranslator):
    decl_index = None
    decl_unique = None

    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ) -> None:

        original_identifier = ctx.variable_identifier().identifier().getText()
        unpacked_dimention = ctx.variable_dimension(0)

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
            if self.decl_type.data_type == DeclTypes.INT:
                self.decl_type.data_type = DeclTypes.ARRAY

                self._translator_ptr.getTranslator("expr").createSizeExpression(
                    original_identifier,
                    dimension_size,
                    ctx.getSourceInterval(),
                )

                self.decl_type.size_expression = self._translator_ptr.translate(
                    "array",
                    original_identifier,
                    DeclTypes.INT,
                    ctx.getSourceInterval(),
                )

        new_decl = Declaration(
            self.decl_type.data_type,
            original_identifier,
            "",
            self.decl_type.size_expression,
            self.decl_type.size[0],
            dimension_size_expression,
            dimension_size,
            ctx.getSourceInterval(),
            name_space_level=self.decl_type.name_space_level,
        )
        self.decl_unique, self.decl_index = self.module.declarations.addElement(
            new_decl
        )

        expression = ctx.expression()

        if not expression:
            return

        self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        self.last_operator = "="
        self._translator_ptr.translate(
            "expr",
            ctx,
        )

    def exit(self, ctx: SystemVerilogParser.Variable_decl_assignmentContext):
        expression = ctx.expression()

        if not expression:
            return
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit()

        declaration = self.module.declarations.getElementByIndex(self.decl_index)

        self.findStruct()

        if self.last_struct is not None:
            self.last_struct.elements.addElement(declaration)
            beh_index = self.last_struct.getLastBehaviorIndex()

            if beh_index is not None and assign_name is not None:
                self.last_struct.behavior[beh_index].addBody(
                    BodyElement(
                        assign_name,
                        action_pointer,
                        ElementsTypes.ACTION_ELEMENT,
                    )
                )
        else:
            if self.decl_unique:
                declaration.expression = assign_name
                declaration.action = action_pointer
