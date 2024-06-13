from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from listener.system_verilog_listener import SVListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from utils import printWithColor, Color


class SystemVerilogFinder:
    def setUp(self, data):
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def startTranslate(self):
        printWithColor("Tranlation process start... \n", Color.ORANGE)
        listener = SVListener()
        self.walker.walk(listener, self.tree)
        printWithColor("Tranlation process finished! \n", Color.ORANGE)
        return listener.module
