import time
import difflib
import traceback
import sys
import shutil
import os
from sv2aplan_tool import start
from utils import Color, format_time, printWithColor, switchRemovePrints


def remove_directory(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        shutil.rmtree(directory_path)
        printWithColor(f"Directory {directory_path} has been removed.\n", Color.ORANGE)
    else:
        printWithColor(f"Directory {directory_path} does not exist.\n", Color.ORANGE)


def compare_files(file1_path, file2_path):
    with open(file1_path, "r", encoding="utf-8") as file1, open(
        file2_path, "r", encoding="utf-8"
    ) as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()

    diff = difflib.unified_diff(
        file1_lines, file2_lines, fromfile=file1_path, tofile=file2_path, lineterm=""
    )
    differences = list(diff)

    return differences


def compare_aplan(path1, path2):
    result = False
    names_array = [
        "project.act",
        "project.behp",
        "project.env_descript",
        "project.evt_descript",
    ]
    for element in names_array:
        last_char = path1[-1]
        if last_char != os.sep:
            path1 += os.sep
        file1_path = path1 + element

        last_char = path2[-1]
        if last_char != os.sep:
            path2 += os.sep
        file2_path = path2 + element

        differences = compare_files(file1_path, file2_path)
        if differences:
            printWithColor(f"File {element} differences: \n", Color.RED)
            for diff in differences:
                printWithColor(f"{diff}\n", Color.RED)
            result = True
        else:
            printWithColor(f"Files {element} are the same \n", Color.BLUE)

    return result


def run_test(test_number, source_file, result_path, aplan_code_path):
    printWithColor(
        f"\n------------------------------------ TEST {test_number} ------------------------------------\n",
        Color.PURPLE,
    )
    test_start_time = time.time()
    try:
        printWithColor(f"Source file : {source_file} \n", Color.BLUE)
        switchRemovePrints(True)
        start(source_file, result_path)
        switchRemovePrints(False)
        differences_found = compare_aplan(aplan_code_path, result_path)
        if differences_found:
            printWithColor(f"Test {test_number} found differences.\n", Color.RED)
            return True
    except Exception as e:
        printWithColor(f"Test {test_number} finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return True
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
    return False


def start_unit_test():
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

    test_definitions = [
        (
            "examples/sv_example_1/sv_example_1.sv",
            "examples/sv_example_1/test_result",
            "examples/sv_example_1/aplan",
        ),
        (
            "examples/sv_example_2/sv_example_2.sv",
            "examples/sv_example_2/test_result",
            "examples/sv_example_2/aplan",
        ),
        (
            "examples/if_statemens/if_statement_1/if_statement_1.sv",
            "examples/if_statemens/if_statement_1/test_result",
            "examples/if_statemens/if_statement_1/aplan",
        ),
        (
            "examples/if_statemens/if_statement_2/if_statement_2.sv",
            "examples/if_statemens/if_statement_2/test_result",
            "examples/if_statemens/if_statement_2/aplan",
        ),
        (
            "examples/assert/assert.sv",
            "examples/assert/test_result",
            "examples/assert/aplan",
        ),
        (
            "examples/loops/loop_1/loop_1.sv",
            "examples/loops/loop_1/test_result",
            "examples/loops/loop_1/aplan",
        ),
        (
            "examples/loops/loop_2/loop_2.sv",
            "examples/loops/loop_2/test_result",
            "examples/loops/loop_2/aplan",
        ),
    ]

    for test_number, data in enumerate(test_definitions):
        source_file, result_path, aplan_code_path = data
        if run_test(test_number + 1, source_file, result_path, aplan_code_path):
            failed_tests.append(test_number + 1)

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
        sys.exit(start_unit_test())
    except Exception as e:
        printWithColor("Tests errors: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
