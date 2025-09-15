from Core.src.tools.tool import BaseTool
import argparse

import traceback
import sys

from translator.translation_mngr import TranslationManager


class Sv2AplanTool(BaseTool):
    def __init__(self):
        super().__init__(name="system verilog to aplan")
        self.setType("sv")
        self.setTranslationMngr(TranslationManager())

    def translate(self, path_to_sv, res_path):
        try:
            self.start(path_to_sv, res_path)
        except Exception as e:
            self.logger.error(
                "Program finished with error:",
            )
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
