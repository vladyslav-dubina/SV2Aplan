import argparse

from tool.tool import Sv2AplanTool


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This program is a translator from the system verilog language to the AVM algebraic model.\nAuthors:  \n1. Vlad Dubina (https://github.com/vladyslav-dubina)"
    )
    parser.add_argument("path_to_sv", help="Path to system verilog(.sv) file")
    parser.add_argument(
        "-rpath",
        metavar="",
        help='Path to result folder. If not entered, the "results" folder will be created.',
        nargs="?",
    )

    args = parser.parse_args()
    tool = Sv2AplanTool()

    tool.start(args.path_to_sv, args.rpath)
