from typing import List
import typing
from classes.parametrs import Parametr, ParametrArray
from translator.classes.base_translator import BaseTranslator


class ParametrArrayTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        parametrs: List[str],
    ) -> ParametrArray:
        result: ParametrArray = ParametrArray()
        for element in parametrs:
            result.addElement(
                Parametr(
                    element,
                    "var",
                )
            )
        return result
