
import argparse
from utils import Color, format_time, printWithColor
from program.program import Program
import time
import traceback
import sys


def main(path_to_sv, path_to_aplan_result):
    printWithColor(
        '\n-------------------------SV TO APLAN TRANSLATOR START-------------------------\n', Color.CYAN)
    start_time = time.time()
    tmp = "Program start time: " + \
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))
    printWithColor(tmp, Color.GREEN)
    printWithColor(
        '\n----------------------------------MAIN PROGRAM---------------------------------\n', Color.CYAN)
    try:
        program = Program(path_to_aplan_result)
        program.setUp(path_to_sv)
        analyze_result = program.finder.startTranslate()
        program.setData(analyze_result)
        program.createAplanFiles()
    except Exception as e:
        printWithColor("Program finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
    printWithColor(
        '\n-------------------------------------------------------------------------------\n', Color.CYAN)
    end_time = time.time()
    execution_time = end_time - start_time
    tmp = "Program end time: " + \
        time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))
    printWithColor(tmp, Color.GREEN)
    printWithColor("Program execution time: " +
                   format_time(execution_time), Color.GREEN)
    printWithColor(
        '\n--------------------------SV TO APLAN TRANSLATOR END---------------------------\n', Color.CYAN)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translator from the system verilog language to the AVM algebraic model.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)")
    parser.add_argument(
        "path_to_sv", help="Path to system verilog(.sv) file")
    parser.add_argument(
        "-rpath", metavar="", help='Path to result folder. If not entered, the "results" folder will be created.', nargs='?')
    args = parser.parse_args()

    try:
        main(args.path_to_sv, args.rpath)
    except Exception as e:
        printWithColor("Program finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
