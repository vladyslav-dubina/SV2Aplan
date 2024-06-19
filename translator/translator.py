from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from listener.system_verilog_listener import SVListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from utils import printWithColor, Color
from program.program import Program
from classes.module_call import ModuleCall


class SystemVerilogFinder:
    def setUp(self, data):
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def startTranslate(self, program: Program, module_call: ModuleCall | None):
        printWithColor(f"Tranlation process start... \n", Color.ORANGE)
        listener = SVListener(program, module_call)
        self.walker.walk(listener, self.tree)
        printWithColor(
            f"Tranlation process finished! ({program.file_path}) \n", Color.ORANGE
        )
        return listener.module.ident_uniq_name
