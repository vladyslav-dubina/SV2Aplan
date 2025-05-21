from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray, RangeTypes
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replaceValueParametrsCalls


class ParametrsCallTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, expression) -> str:
        parametrs_array = self.module.value_parametrs.copy()

        packages = self.module.packages_and_objects.getElementsIE(
            include=ElementsTypes.PACKAGE_ELEMENT,
            exclude_ident_uniq_name=self.module.ident_uniq_name,
        )

        for element in packages.getElements():
            parametrs_array += element.value_parametrs.copy()

        return replaceValueParametrsCalls(parametrs_array, expression)
