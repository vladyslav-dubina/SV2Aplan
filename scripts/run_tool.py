import argparse
from pathlib import Path

from tool.tool import Sv2AplanTool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translator from the system verilog language to the AVM algebraic model.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)"
    )
    parser.add_argument("fpath", help="Path to system verilog(.sv) file")
    parser.add_argument(
        "-rpath",
        metavar="",
        help='Path to result folder. If not entered, the "results" folder will be created.',
        nargs="?",
    )

    args = parser.parse_args()
    tool = Sv2AplanTool()

    file_path = Path(args.fpath) if args.fpath else None
    result_path = Path(args.rpath) if args.rpath else None

    tool.start(file_path, result_path)
