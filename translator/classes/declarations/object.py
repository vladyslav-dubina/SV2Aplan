from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class ObjectDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        class_name: str,
        identifier: str,
        source_interval: Tuple[int, int],
    ) -> None:
        class_module = self.modules.findElement(class_name.upper())
        class_module = class_module.copyPart()
        index = self.modules.addElement(class_module)
        object = self.modules.getElementByIndex(index)
        object.element_type = ElementsTypes.OBJECT_ELEMENT
        object.identifier = class_name.upper()
        object.identifier_upper = object.identifier
        object.ident_uniq_name = identifier
        object.ident_uniq_name_upper = object.ident_uniq_name.upper()
        object.source_interval = source_interval
        self.module.packages_and_objects.addElement(object)
        Counters_Object.incrieseCounter(CounterTypes.OBJECT_COUNTER)
