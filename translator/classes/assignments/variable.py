import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclType, DeclTypes, Declaration
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement, Protocol
from AppModule.app.classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator


class VariableDeclTranslator(BaseTranslator):
    decl_index = None
    decl_unique = None

    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def reset(self):
        self.decl_index = None
        self.decl_unique = None

    def translate(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ) -> None:
        original_identifier = ctx.variable_identifier().identifier().getText()

        dimension_size = 0
        dimension_size_expression = ""
        decl_type = self.decl_type_array.getLastElement()
        if decl_type:
            (
                size_expression,
                aplan_vector_size,
                dimension_size_expression,
                dimension_size,
                vector_size_tuple,
            ) = self._process_dimensions(
                ctx.variable_dimension(0),
                None,
            )

            if dimension_size > 0 and decl_type.data_type == DeclTypes.INT:
                decl_type.data_type = DeclTypes.ARRAY
                if not decl_type.size_expression:
                    self._translator_ptr.getTranslator("expr").createSizeExpression(
                        original_identifier,
                        dimension_size,
                        ctx.getSourceInterval(),
                    )
                    decl_type.size_expression = self._translator_ptr.translate(
                        "array",
                        original_identifier,
                        DeclTypes.INT,
                        ctx.getSourceInterval(),
                    )

            new_decl = Declaration(
                decl_type.data_type,
                original_identifier,
                "",
                decl_type.size_expression,
                decl_type.size[0],
                dimension_size_expression,
                dimension_size,
                ctx.getSourceInterval(),
                name_space_level=decl_type.name_space_level,
            )

            if decl_type.inside_the_struct:
                typedef: Typedef = self.getLastTypedef()
                if typedef:
                    typedef.declarations.addElement(new_decl)
            else:
                (
                    self.decl_unique,
                    self.decl_index,
                ) = self.design_unit.declarations.addElement(new_decl)

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

        declaration = None
        if self.decl_index:
            declaration = self.design_unit.declarations.getElementByIndex(
                self.decl_index
            )

        self.findStruct()

        if self.last_struct is not None:
            if declaration:
                self.last_struct.elements.addElement(declaration)

            beh_index = self.last_struct.getLastBehaviorIndex()
            if beh_index is not None and assign_name:
                self.last_struct.behavior[beh_index].addBodyElement(
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
            else:
                assign_b = "{}_B".format(action_pointer.getName(to_upper=True))
                struct_assign: Protocol = Protocol(
                    assign_b,
                    ctx.getSourceInterval(),
                    ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                )

                struct_assign.addBodyElement(
                    BodyElement(
                        assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )
                self.design_unit.out_of_block_elements.addElement(struct_assign)

        self.reset()
