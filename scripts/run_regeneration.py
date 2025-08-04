import argparse

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

    tool.regeneration_start(args.e_path, args.path)
