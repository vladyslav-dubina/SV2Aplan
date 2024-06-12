import time
import traceback
import sys
import shutil
import os
from sv2aplan_tool import start
from utils import Color, format_time, printWithColor, switchRemovePrints


def run_generation(test_number, source_file, result_path):
    printWithColor(
        f"\n--------------------------------- GENERATION {test_number} ---------------------------------\n",
        Color.PURPLE,
    )
    test_start_time = time.time()
    try:
        switchRemovePrints(True)
        start(source_file, result_path)
        switchRemovePrints(False)
    except Exception as e:
        printWithColor(f"Generation {test_number} finished with error: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
        return True
    finally:
        test_end_time = time.time()
        test_execution_time = test_end_time - test_start_time
        printWithColor(
            f"Generation {test_number} execution time: "
            + format_time(test_execution_time),
            Color.GREEN,
        )
        printWithColor(
            "\n--------------------------------------------------------------------------------\n",
            Color.CYAN,
        )
    return False


def regeneration_start():
    failed_generations = []
    printWithColor(
        "\n------------------------------ GENERATON START --------------------------------\n",
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
            1,
            "examples/sv_example_1/sv_example_1.sv",
            "examples/sv_example_1/aplan",
        ),
        (
            2,
            "examples/sv_example_2/sv_example_2.sv",
            "examples/sv_example_2/aplan",
        ),
        (
            3,
            "examples/sv_example_3/sv_example_3.sv",
            "examples/sv_example_3/aplan",
        ),
    ]

    for test_number, source_file, result_path in test_definitions:
        if run_generation(test_number, source_file, result_path):
            failed_generations.append(test_number)

    end_time = time.time()
    execution_time = end_time - start_time
    printWithColor(
        "Generation process end time: "
        + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time)),
        Color.GREEN,
    )
    printWithColor(
        "Generation process execution time: " + format_time(execution_time), Color.GREEN
    )

    if not failed_generations:
        printWithColor(
            "\n------------------------------- GENERATON SUCCESS -----------------------------\n",
            Color.PURPLE,
        )
        return 0
    else:
        printWithColor(
            "\n------------------------------- GENERATON FAILED -----------------------------\n",
            Color.PURPLE,
        )
        printWithColor(f"Errors in generations: {failed_generations}\n", Color.RED)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(regeneration_start())
    except Exception as e:
        printWithColor("Generation errors: \n", Color.RED)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
