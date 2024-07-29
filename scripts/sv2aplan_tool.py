import argparse
import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.utils import (
    Color,
    format_time,
    printWithColor,
    programCountersDeinit,
)
from program.program import Program
from translator.translator import SystemVerilogFinder


def is_sv_file(path: str):
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist")

    if os.path.isfile(path) and path.endswith(".sv"):
        return True
    else:
        raise ValueError(f"Path '{path}' is not a .sv file")


def start(path, path_to_aplan_result):
    result = False
    printWithColor(
        "\n-------------------------SV TO APLAN TRANSLATOR START-------------------------\n",
        Color.CYAN,
    )
    start_time = time.time()
    tmp = "Program start time: " + time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(start_time)
    )
    printWithColor(tmp, Color.GREEN)
    printWithColor(
        "\n----------------------------------MAIN PROGRAM---------------------------------\n",
        Color.CYAN,
    )
    try:
        program = Program(path_to_aplan_result)
        if is_sv_file(path):
            file_data = program.readFileData(path)
            finder = SystemVerilogFinder()
            finder.setUp(file_data)
            finder.startTranslate(program, None)
        program.createResDir()
        program.createAplanFiles()
    except Exception as e:
        result = True
        printWithColor("Program finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
    printWithColor(
        "\n-------------------------------------------------------------------------------\n",
        Color.CYAN,
    )
    end_time = time.time()
    execution_time = end_time - start_time
    tmp = "Program end time: " + time.strftime(
        "%Y-%m-%d %H:%M:%S", time.localtime(end_time)
    )
    printWithColor(tmp, Color.GREEN)
    printWithColor(
        "Program execution time: " + format_time(execution_time), Color.GREEN
    )
    printWithColor(
        "\n--------------------------SV TO APLAN TRANSLATOR END---------------------------\n",
        Color.CYAN,
    )
    programCountersDeinit()
    return result


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

    try:
        start(args.path_to_sv, args.rpath)
    except Exception as e:
        printWithColor("Program finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
