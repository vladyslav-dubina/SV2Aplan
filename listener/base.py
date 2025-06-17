from AppModule.app.classes.module import Module
from AppModule.app.classes.module_call import ModuleCall

from AppModule.app.utils.counters import Counters
from AppModule.app.utils.logger import Logger
from translator.translator import Translator


class BaseListener:

    translator = Translator()
    counters = Counters()
    logger = Logger()

    @property
    def module(self) -> Module:
        return self.translator._module

    @property
    def module_call(self) -> Module:
        return self.translator.module_call

    def __init__(self, module_call: ModuleCall | None = None):
        self.translator.module_call = module_call
