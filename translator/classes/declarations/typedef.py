from typing import List, Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement


class TypedefDeclTranslator(BaseTranslator):
    need_delete_struct = False
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        type_declaration: SystemVerilogParser.Type_declarationContext | None = (
            ctx.type_declaration()
        )
        if not type_declaration:
            return
        data_type: SystemVerilogParser.Data_typeContext | None = (
            type_declaration.data_type()
        )

        if not (data_type.ENUM() or data_type.struct_union()):
            return
        type_identifier = type_declaration.type_identifier(0)

        if type_declaration.type_identifier(1):
            raise TypeError("Unhandled identifiers count")

        enum_type_identifier = "{0}".format(type_identifier.getText())
        unique_identifier = "{0}_{1}".format(
            enum_type_identifier,
            self.getLastNameSpaceLevel(),
        )

        decl_type = DeclTypes.ENUM_TYPE
        if data_type.struct_union():
            decl_type = DeclTypes.STRUCT_TYPE

        typedef = Typedef(
            enum_type_identifier,
            unique_identifier,
            type_identifier.getSourceInterval(),
            self._program.file_path,
            decl_type,
        )

        self.last_typedef = typedef

        self.addTypedef(typedef)

    def exit(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        if self.need_delete_struct:
            self.need_delete_struct = False
            self._translator_ptr.removeLastStructPointer()

        self.last_typedef = None

    def create(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        arguments: List[Tuple[str, DeclTypes]],
    ):
        typedef = Typedef(
            identifier,
            identifier,
            source_interval,
            self._program.file_path,
            DeclTypes.STRUCT_TYPE,
        )

        element_source_interval = (0, 0)
        for element in arguments:
            new_decl = Declaration(
                element[1],
                element[0],
                "",
                "",
                0,
                "",
                0,
                element_source_interval,
            )
            element_source_interval = (
                element_source_interval[0],
                element_source_interval[1] + 1,
            )
            typedef.declarations.addElement(new_decl)

        self.addTypedef(typedef)


class EnumNameDeclTranslator(BaseTranslator):
    decl_index = None
    decl_unique = None
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def reset(self):
        self.decl_index = None
        self.decl_unique = None

    def translate(self, ctx: SystemVerilogParser.Enum_name_declarationContext) -> None:

        typedef = self.getLastTypedef()
        if typedef:
            identifier = ctx.enum_identifier().getText()
            new_decl = Declaration(
                data_type=DeclTypes.ENUM,
                identifier=identifier,
                source_interval=ctx.getSourceInterval(),
            )

            (
                self.decl_unique,
                self.decl_index,
            ) = typedef.declarations.addElement(new_decl)

            expression: SystemVerilogParser.Constant_expressionContext = (
                ctx.constant_expression()
            )

            if not expression:
                return
            eval_expression = ""
            for element in expression.getChildren():
                element_type = type(element)

                text = element.getText()
                if isinstance(
                    element, SystemVerilogParser.Constant_primaryContext
                ) or isinstance(
                    element, SystemVerilogParser.Constant_expressionContext
                ):
                    if not self.utils.isNumericString(text):
                        constant: Declaration = typedef.declarations.getElement(text)
                        text = constant.expression

                eval_expression += text

            if len(eval_expression) > 0:
                result = eval(eval_expression)
                new_decl.expression = str(result)

    def exit(self, ctx: SystemVerilogParser.Enum_name_declarationContext) -> None:
        # expression = ctx.constant_expression()

        # if not expression:
        #     return

        # (
        #     action_pointer,
        #     assign_name,
        #     source_interval,
        #     uniq_action,
        # ) = self._translator_ptr.getTranslator("expr").exit()

        # declaration = None
        # if self.decl_index is not None:
        #     typedef = self.design_unit.typedefs.getLastElement()
        #     declaration = typedef.declarations.getElementByIndex(self.decl_index)

        # self.findStruct()
        # if self.last_struct is not None:
        #     if declaration:
        #         self.last_struct.elements.addElement(declaration)

        #     beh_index = self.last_struct.getLastBehaviorIndex()
        #     if beh_index is not None and assign_name:
        #         self.last_struct.behavior[beh_index].addBodyElement(
        #             BodyElement(
        #                 assign_name,
        #                 action_pointer,
        #                 ElementsTypes.ACTION_ELEMENT,
        #             )
        #         )

        # else:
        #     if self.decl_unique:
        #         declaration.expression = assign_name
        #         declaration.action = action_pointer
        #     else:
        #         assign_b = "{}_B".format(action_pointer.getName(to_upper=True))
        #         struct_assign: Protocol = Protocol(
        #             assign_b,
        #             ctx.getSourceInterval(),
        #             ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
        #         )

        #         struct_assign.addBodyElement(
        #             BodyElement(
        #                 assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT
        #             )
        #         )
        #         self.design_unit.out_of_block_elements.addElement(struct_assign)

        # self.reset()
        pass
