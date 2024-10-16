import time
import traceback
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.sv2aplan_tool import start
from utils.utils import Color, format_time, printWithColor, switchRemovePrints
from scripts.examples_list import examples_list


def run_generation(test_number, source_file, result_path):
    result = False
    printWithColor(
        f"\n--------------------------------- GENERATION {test_number} ---------------------------------\n",
        Color.PURPLE,
    )
    test_start_time = time.time()
    try:
        printWithColor(f"Source file : {source_file} \n", Color.BLUE)
        switchRemovePrints(True)
        result = start(source_file, result_path)
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
    return result


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

    for test_number, data in enumerate(examples_list):
        source_file, unused_path, result_path = data
        if run_generation(test_number + 1, source_file, result_path):
            failed_generations.append(test_number + 1)

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
