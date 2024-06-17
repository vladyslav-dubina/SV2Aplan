import argparse
import time
import traceback
import sys
import os
import glob
from classes.aplan import Module
from utils import (
    Color,
    format_time,
    printWithColor,
    moduleCounterDeinit,
)
from program.program import Program
from typing import List


def find_sv_files(path: str):
    if not os.path.exists(path):
        raise ValueError(f"Path '{path}' does not exist")

    if os.path.isfile(path) and path.endswith(".sv"):
        return [path]

    elif os.path.isdir(path):
        sv_files = glob.glob(os.path.join(path, "**", "*.sv"), recursive=True)
        return sv_files
    else:
        raise ValueError(
            f"Path '{path}' is not a .sv file or a directory containing .sv files"
        )


def start(path, path_to_aplan_result):
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
        analyze_result: List[Module] = []
        for path_to_sv in find_sv_files(path):
            program.setUp(path_to_sv)
            printWithColor(f"Source file : {path_to_sv} \n", Color.BLUE)
            analyze_result.append(program.finder.startTranslate())
        program.setData(analyze_result)
        program.createResDir()
        program.createAplanFiles()
    except Exception as e:
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
    moduleCounterDeinit()


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
