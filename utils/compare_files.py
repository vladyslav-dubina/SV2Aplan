import difflib
import os
from utils.utils import Color, printWithColor


def compareFiles(file1_path, file2_path):
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


def compareAplanByPathes(path1, path2):
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

        differences = compareFiles(file1_path, file2_path)
        if differences:
            printWithColor(f"File {element} differences: \n", Color.RED)
            for diff in differences:
                printWithColor(f"{diff}\n", Color.RED)
            result = True
        else:
            printWithColor(f"Files {element} are the same \n", Color.BLUE)

    return result
