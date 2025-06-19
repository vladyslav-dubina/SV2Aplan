from typing import Tuple
import typing
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.utils.counters import CounterTypes
from translator.classes.base_translator import BaseTranslator


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
            "{0}_{1}".format(name_part, self.counters.get(counter_type)),
            "",
            size_expression,
            0,
            "",
            0,
            source_interval,
        )
        uniq, index = self.design_unit.declarations.addElement(decl)
        if uniq:
            self.counters.incriese(counter_type)

        return self.design_unit.declarations.getElementByIndex(index)
