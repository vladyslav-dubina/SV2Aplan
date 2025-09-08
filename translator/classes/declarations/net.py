import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement
from AppModule.app.classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator


class NewDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Net_declarationContext) -> None:
        data_type = ctx.data_type_or_implicit()
        unpacked_dimention = ctx.unpacked_dimension(0)
        dimension_size = 0
        dimension_size_expression = ""
        if unpacked_dimention is not None:
            dimension = unpacked_dimention.getText()
            dimension_size_expression = dimension
            dimension = self.str_formater.replaceValueParametrsCalls(
                self.design_unit.value_parametrs, dimension
            )
            dimension_size = self.utils.extractDimentionSize(dimension)

        aplan_vector_size = [0]
        size_expression = ""
        if data_type:
            size_expression = data_type.getText()
            data_type = self.str_formater.replaceValueParametrsCalls(
                self.design_unit.value_parametrs, data_type.getText()
            )
            vector_size = self.utils.extractVectorSize(data_type)
            if vector_size is not None:
                aplan_vector_size = self.utils.vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

        if ctx.net_type() is not None:
            data_type = ctx.net_type().getText()
        elif ctx.data_type_or_implicit() is not None:
            data_type = ctx.data_type_or_implicit().getText()
        elif ctx.net_type_identifier() is not None:
            data_type = ctx.net_type_identifier().getText()
            size_expression = data_type

        if data_type is not None:
            types = self.design_unit.typedefs.getElementsIE(
                file_path=self._program.file_path
            ).getElements()

            types += self._program.typedefs.getElementsIE(
                file_path=self._program.file_path
            ).getElements()

            types += self._program.design_units.getElementsIE(
                include=ElementsTypes.CLASS_ELEMENT
            ).getElements()

            packages = self.design_unit.packages_and_objects.getElementsIE(
                include=ElementsTypes.PACKAGE_ELEMENT
            )
            for package in packages.getElements():
                types += package.typedefs.getElementsIE().getElements()

            data_check_type = DeclTypes.checkType(data_type, types)

            # change type names for unique type names for structs

            if data_check_type == DeclTypes.ENUM or data_check_type == DeclTypes.STRUCT:
                for element in types:
                    if isinstance(element, Typedef):
                        if element.identifier == size_expression:
                            size_expression = element.unique_identifier

            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                if data_check_type is DeclTypes.CLASS:
                    self._translator_ptr.translate(
                        "obj_decl", size_expression, identifier, ctx.getSourceInterval()
                    )

                else:
                    assign_name = ""
                    decl_unique, decl_index = self.design_unit.declarations.addElement(
                        Declaration(
                            data_check_type,
                            identifier,
                            assign_name,
                            size_expression,
                            aplan_vector_size[0],
                            dimension_size_expression,
                            dimension_size,
                            elem.getSourceInterval(),
                            name_space_level=self.getLastNameSpaceLevel(),
                        )
                    )

                    if not elem.expression():
                        return

                    if data_check_type == DeclTypes.ENUM:
                        for element in self.design_unit.typedefs.getElements():

                            if element.unique_identifier == size_expression:
                                self.createStatement(
                                    size_expression.upper(),
                                    ElementsTypes.NONE_ELEMENT,
                                    None,
                                )
                                self.findStruct()

                                beh_index = self.last_struct.getLastBehaviorIndex()

                                for enum_elem in element.declarations.getElements():
                                    if beh_index is not None and enum_elem.expression:
                                        self.last_struct.behavior[
                                            beh_index
                                        ].addBodyElement(
                                            BodyElement(
                                                enum_elem.expression,
                                                enum_elem.action,
                                                ElementsTypes.ACTION_ELEMENT,
                                            )
                                        )

                    expression = elem.expression().getText()
                    if expression:
                        raise Exception("Unhandled")
                        (
                            action_pointer,
                            assign_name,
                            source_interval,
                            uniq_action,
                        ) = self._translator_ptr.translate(
                            "expr",
                            elem.getText(),
                            ElementsTypes.ASSIGN_ELEMENT,
                        )
                        declaration = self.design_unit.declarations.getElementByIndex(
                            decl_index
                        )
                        declaration.expression = assign_name
                        declaration.action = action_pointer

    def exit(self, ctx: SystemVerilogParser.Net_declarationContext) -> None:
        pass
