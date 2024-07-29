from utils.utils import (
    Color,
    printWithColor,
)
from utils.compare_files import compareAplanByPathes

aplan_code_path = "examples/code_patch/aplan"
result_path = "tmp/"

differences_found = compareAplanByPathes(aplan_code_path, result_path, [".act"])
if differences_found:
    printWithColor(f"Found differences.\n", Color.RED)
