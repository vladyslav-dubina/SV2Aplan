from Core.src.classes.design_unit import DesignUnit
from Core.src.classes.design_unit_call import DesignUnitCall

from Core.src.utils.counters import Counters
from Core.src.logger.logger import Logger, LoggerManager
from translator.translator import Translator


class BaseListener:
    translator = Translator()
    counters = Counters()

    @property
    def design_unit(self) -> DesignUnit:
        return self.translator._design_unit

    @property
    def design_unit_call(self) -> DesignUnitCall:
        return self.translator.design_unit_call

    def __init__(self, design_unit_call: DesignUnitCall | None = None):
        self.translator.design_unit_call = design_unit_call
        logger_manager = LoggerManager()
        self.logger = logger_manager.getLogger(self.__class__.__qualname__)
