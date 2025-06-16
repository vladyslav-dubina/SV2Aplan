from AppModule.app.tools.tool import BaseTool
import argparse

import traceback
import sys

from translator.translation_mngr import TranslationManager


class Sv2AplanTool(BaseTool):
    def __init__(self):
        super().__init__(name="system verilog to aplan")
        self.translation_mngr = TranslationManager()
        self._type = "sv"

    def translate(self, path_to_sv, res_path):
        try:
            self.start(path_to_sv, res_path)
        except Exception as e:
            self.logger.error(
                "Program finished with error:",
            )
            traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translator from the system verilog language to the AVM algebraic model.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)"
    )
    parser.add_argument("path_to_sv", help="Path to system verilog(.sv) file")
    parser.add_argument(
        "-rpath",
        metavar="",
        help='Path to result folder. If not entered, the "results" folder will be created.',
        nargs="?",
    )
    args = parser.parse_args()
    tool = Sv2AplanTool()

    tool.start(args.path_to_sv, args.rpath)
