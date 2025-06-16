from typing import Tuple
import typing
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class DeclarationTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        name_part,
        type: DeclTypes,
        counter_type: CounterTypes,
        source_interval: Tuple[int, int],
        size_expression: str = "",
    ) -> None:
        decl = Declaration(
            type,
            "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type)),
            "",
            size_expression,
            0,
            "",
            0,
            source_interval,
        )
        uniq, index = self.module.declarations.addElement(decl)
        if uniq:
            Counters_Object.incriese(counter_type)

        return self.module.declarations.getElementByIndex(index)
