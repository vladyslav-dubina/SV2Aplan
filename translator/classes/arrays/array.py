from typing import Tuple
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import Counters_Object


class ArrayTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        identifier: str,
        decl_type: DeclTypes,
        source_interval: Tuple[int, int],
    ) -> str:
        enum_type_identifier = "{0}".format(identifier)
        unique_identifier = "{0}_{1}".format(
            enum_type_identifier,
            Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        typedef = Typedef(
            enum_type_identifier,
            unique_identifier,
            source_interval,
            self._program.file_path,
            DeclTypes.STRUCT_TYPE,
        )

        new_decl = Declaration(
            DeclTypes.INT,
            "size",
            "",
            "",
            0,
            "",
            0,
            (0, 0),
        )
        typedef.declarations.addElement(new_decl)

        new_decl = Declaration(
            decl_type,
            "value",
            "",
            "",
            0,
            "",
            1,
            (0, 1),
        )
        typedef.declarations.addElement(new_decl)

        if self.module:
            decl_unique, decl_index = self.module.typedefs.addElement(typedef)
        else:
            decl_unique, decl_index = self._program.typedefs.addElement(typedef)

        return unique_identifier


    def