import argparse
from pathlib import Path

from tool.tool import Sv2AplanTool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translation examples regenerator.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)"
    )

    parser.add_argument(
        "-e_path",
        metavar="",
        help="Path to system verilog examples list file",
        nargs="?",
    )

    parser.add_argument(
        "-path",
        metavar="",
        help="Path to system verilog(.sv) file",
        nargs="?",
    )

    args = parser.parse_args()
    tool = Sv2AplanTool()

    file_path = Path(args.e_path) if args.e_path else None
    result_path = Path(args.rpath) if args.rpath else None

    tool.regeneration_start(Path(args.e_path), Path(args.rpath))
