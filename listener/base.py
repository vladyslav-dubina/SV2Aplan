from classes.module import Module
from classes.module_call import ModuleCall
from translator.translator import Translator


class BaseListener:

    translator = Translator()

    @property
    def module(self) -> Module:
        return self.translator._module

    @property
    def module_call(self) -> Module:
        return self.translator.module_call


    def __init__(self, module_call: ModuleCall | None = None):
        self.translator.module_call = module_call
