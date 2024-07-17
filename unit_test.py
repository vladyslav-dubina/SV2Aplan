import time
import traceback
import sys
import shutil
import os
from sv2aplan_tool import start
from utils.utils import Color, format_time, printWithColor, switchRemovePrints
from utils.compare_files import compareAplanByPathes


def remove_directory(directory_path):
    if os.path.exists(directory_path) and os.path.isdir(directory_path):
        shutil.rmtree(directory_path)
        printWithColor(f"Directory {directory_path} has been removed.\n", Color.ORANGE)
    else:
        printWithColor(f"Directory {directory_path} does not exist.\n", Color.ORANGE)


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
        differences_found = compareAplanByPathes(aplan_code_path, result_path)
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
            "examples/initial/initial.sv",
            "examples/initial/test_result",
            "examples/initial/aplan",
        ),
        (
            "examples/assigns/assign_1/assign_1.sv",
            "examples/assigns/assign_1/test_result",
            "examples/assigns/assign_1/aplan",
        ),
        (
            "examples/parametrs/parametrs_1/parametrs_1.sv",
            "examples/parametrs/parametrs_1/test_result",
            "examples/parametrs/parametrs_1/aplan",
        ),
        (
            "examples/assert/assert.sv",
            "examples/assert/test_result",
            "examples/assert/aplan",
        ),
        (
            "examples/always/always_@*/always_@*.sv",
            "examples/always/always_@*/test_result",
            "examples/always/always_@*/aplan",
        ),
        (
            "examples/always/always_without_sensetive/always_without_sensetive.sv",
            "examples/always/always_without_sensetive/test_result",
            "examples/always/always_without_sensetive/aplan",
        ),
        (
            "examples/case/case.sv",
            "examples/case/test_result",
            "examples/case/aplan",
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
            "examples/loops/loop_1/loop_1.sv",
            "examples/loops/loop_1/test_result",
            "examples/loops/loop_1/aplan",
        ),
        (
            "examples/loops/loop_2/loop_2.sv",
            "examples/loops/loop_2/test_result",
            "examples/loops/loop_2/aplan",
        ),
        (
            "examples/loops/while_1/while_1.sv",
            "examples/loops/while_1/test_result",
            "examples/loops/while_1/aplan",
        ),
        (
            "examples/loops/while_2/while_2.sv",
            "examples/loops/while_2/test_result",
            "examples/loops/while_2/aplan",
        ),
        (
            "examples/loops/foreach/foreach.sv",
            "examples/loops/foreach/test_result",
            "examples/loops/foreach/aplan",
        ),
        (
            "examples/call/call_1/call_2.sv",
            "examples/call/call_1/test_result",
            "examples/call/call_1/aplan",
        ),
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
