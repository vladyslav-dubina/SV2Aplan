import time
import traceback
import sys
import shutil
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.sv2aplan_tool import start
from utils.utils import Color, format_time, printWithColor, switchRemovePrints
from utils.compare_files import compareAplanByPathes
from scripts.examples_list import examples_list


def remove_directory(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        shutil.rmtree(directory_path)
        printWithColor(f"Directory {directory_path} has been removed.\n", Color.ORANGE)
    else:
        printWithColor(f"Directory {directory_path} does not exist.\n", Color.ORANGE)


def run_test(test_number, source_file, result_path, aplan_code_path):
    result = False
    printWithColor(
        f"\n------------------------------------ TEST {test_number} ------------------------------------\n",
        Color.PURPLE,
    )
    test_start_time = time.time()
    try:
        printWithColor(f"Source file : {source_file} \n", Color.BLUE)
        switchRemovePrints(True)
        result = start(source_file, result_path)
        switchRemovePrints(False)

        if result:
            printWithColor(f"Test {test_number} finished with error: \n", Color.RED)

        differences_found = compareAplanByPathes(aplan_code_path, result_path)
        if differences_found:
            printWithColor(f"Test {test_number} found differences.\n", Color.RED)
            result = True
    except Exception as e:
        printWithColor(f"Test {test_number} finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        result = True
    finally:
        remove_directory(result_path)
        test_end_time = time.time()
        test_execution_time = test_end_time - test_start_time
        printWithColor(
            f"Test {test_number} execution time: " + format_time(test_execution_time),
            Color.GREEN,
        )
        printWithColor(
            "\n--------------------------------------------------------------------------------\n",
            Color.CYAN,
        )
    return result


def start_tests():
    failed_tests = []
    printWithColor(
        "\n--------------------------------- TESTS START ----------------------------------\n",
        Color.PURPLE,
    )
    start_time = time.time()
    printWithColor(
        "Testing start time: "
        + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time)),
        Color.GREEN,
    )

    for test_number, data in enumerate(examples_list):
        source_file, result_path, aplan_code_path = data
        if run_test(test_number + 1, source_file, result_path, aplan_code_path):
            failed_tests.append((test_number + 1, source_file))

    end_time = time.time()
    execution_time = end_time - start_time
    printWithColor(
        "Testing end time: "
        + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
        Color.GREEN,
    )
    printWithColor(
        "Testing execution time: " + format_time(execution_time), Color.GREEN
    )

    if not failed_tests:
        printWithColor(
            "\n---------------------------------- TESTS SUCCESS -------------------------------\n",
            Color.PURPLE,
        )
        return 0
    else:
        printWithColor(
            "\n---------------------------------- TESTS FAILED -------------------------------\n",
            Color.PURPLE,
        )
        printWithColor(f"Errors in tests: {failed_tests}\n", Color.RED)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(start_tests())
    except Exception as e:
        printWithColor("Tests errors: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
