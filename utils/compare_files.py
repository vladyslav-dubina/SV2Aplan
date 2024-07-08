import difflib
import os
import glob

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


def compareAplanByPathes(path1, path2, extensions_to_compare: str | None = None):
    result = False
    if extensions_to_compare == None:
        extensions_to_compare = [".act", ".behp", ".env_descript", ".evt_descript"]
    for ext in extensions_to_compare:
        files1 = glob.glob(os.path.join(path1, "*" + ext))
        files2 = glob.glob(os.path.join(path2, "*" + ext))

        for file1 in files1:
            filename = os.path.basename(file1)
            file2 = os.path.join(path2, filename)
            if file2 in files2:
                differences = compareFiles(file1, file2)
                if differences:
                    printWithColor(f"File {filename} differences: \n", Color.RED)
                    for diff in differences:
                        printWithColor(f"{diff}\n", Color.RED)
                    result = True
                else:
                    printWithColor(f"Files {filename} are the same \n", Color.BLUE)
            else:
                printWithColor(f"File {filename} not found in {path2} \n", Color.RED)

    return result
