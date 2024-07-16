from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree

from translator.system_verilog_to_aplan import SV2aplan


def extractSensetiveImpl(self: SV2aplan, ctx):
    res = ""
    for child in ctx.getChildren():
        if type(child) is SystemVerilogParser.Edge_identifierContext:
            index = child.getText().find("negedge")
            if index != -1:
                res += "!"
        elif type(child) is Tree.TerminalNodeImpl:
            index = child.getText().find("or")
            if index != -1:
                res += " || "
            index = child.getText().find("and")
            if index != -1:
                res += " && "
        elif type(child) is SystemVerilogParser.IdentifierContext:
            res += self.module.findAndChangeNamesToAgentAttrCall(child.getText())
        else:
            res += self.extractSensetive(child)
    return res
