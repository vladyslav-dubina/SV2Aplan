import typing

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

    @property
    def inside_the_task(self) -> bool:
        return self._translator_ptr._inside_the_task

    @inside_the_function.setter
    def inside_the_function(self, value: bool):
        self._translator_ptr._inside_the_function = value

    @inside_the_task.setter
    def inside_the_task(self, value: bool):
        self._translator_ptr._inside_the_task = value
