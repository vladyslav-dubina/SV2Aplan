from Core.src.tools.cli import ToolCLI
from tool.tool import Sv2AplanTool


if __name__ == "__main__":
    cli = ToolCLI(
        tool_class=Sv2AplanTool,
        description="A comprehensive tool for translating SystemVerilog to an AVM algebraic model.",
    )
    cli.run()
