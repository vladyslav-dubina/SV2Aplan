from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.design_unit_call import DesignUnitCall

from AppModule.app.utils.counters import Counters
from AppModule.app.utils.logger import Logger
from translator.translator import Translator


class BaseListener:
    translator = Translator()
    counters = Counters()
    logger = Logger()

    @property
    def design_unit(self) -> DesignUnit:
        return self.translator._design_unit

    @property
    def design_unit_call(self) -> DesignUnitCall:
        return self.translator.design_unit_call

    def __init__(self, design_unit_call: DesignUnitCall | None = None):
        self.translator.design_unit_call = design_unit_call
