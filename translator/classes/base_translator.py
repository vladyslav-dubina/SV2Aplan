import typing

from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.structure import StructureArray

if typing.TYPE_CHECKING:
    from translator.translator import Translator

from classes.module import Module, ModuleArray
from program.program import Program
from classes.module_call import ModuleCall


class BaseTranslator:
    def __init__(self, translator: "Translator"):

        self._translator_ptr = translator
        self._program = Program()

    def translate(self, ctx) -> None:
        raise TypeError("Run base translator")

    def createStatement(self,
        name,
        element_type:ElementsTypes,
        sensetive: str | None = None,
        counter_type: CounterTypes = CounterTypes.UNIQ_NAMES_COUNTER,
    ): self._translator_ptr.createStatement(name, element_type, sensetive,counter_type)

    def extractSensetive(self, ctx):
        return self._translator_ptr.extractSensetive(ctx)
    @property
    def module_call(self) -> ModuleCall:
        return self._translator_ptr.module_call

    @property
    def modules(self) -> ModuleArray:
        return self._program.modules

    @property
    def module(self) -> Module:
        return self._translator_ptr._module

    @property
    def structure_pointer_list(self) -> StructureArray:
        return self._translator_ptr._structure_pointer_list

    @property
    def inside_the_function(self) -> bool:
        return self._translator_ptr._inside_the_function

    @inside_the_function.setter
    def inside_the_function(self, value: bool):
        self._translator_ptr._inside_the_function = value

    @property
    def inside_the_task(self) -> bool:
        return self._translator_ptr._inside_the_task

    @inside_the_task.setter
    def inside_the_task(self, value: bool):
        self._translator_ptr._inside_the_task = value

    def getLastNameSpaceLevel(self) -> bool:
        return self._translator_ptr.getLastNameSpaceLevel()

    def getProtocolParams(self):
        return self._translator_ptr.getProtocolParams()

    @inside_the_task.setter
    def inside_the_task(self, value: bool):
        self._translator_ptr._inside_the_task = value
