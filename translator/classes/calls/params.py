import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from translator.classes.base_translator import BaseTranslator


class ParametrsCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, expression) -> str:
        parametrs_array = self.design_unit.value_parametrs.copy()

        packages = self.design_unit.packages_and_objects.getElementsIE(
            include=ElementsTypes.PACKAGE_ELEMENT,
            exclude_ident_uniq_name=self.design_unit.ident_uniq_name,
        )

        for element in packages.getElements():
            parametrs_array += element.value_parametrs.copy()

        return self.str_formater.replaceValueParametrsCalls(parametrs_array, expression)
