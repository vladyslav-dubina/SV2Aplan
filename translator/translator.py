from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from listener.system_verilog_listener import SVListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from utils.utils import printWithColor, printWithColors, Color
from program.program import Program
from classes.module_call import ModuleCall


class SystemVerilogFinder:
    def setUp(self, data):
        printWithColor("Set up tranlator environment \n", Color.ORANGE)
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def startTranslate(self, program: Program, module_call: ModuleCall | None = None):
        printWithColor(f"Tranlation process start... \n", Color.ORANGE)

        listener = SVListener(program, module_call)
        self.walker.walk(listener, self.tree)
        printWithColor(f"File tranlation process finished! \n", Color.ORANGE)
        printWithColors(
            [
                ("File ", Color.ORANGE),
                (f"{program.file_path}", Color.PURPLE),
                (" tranlation process finished! \n", Color.ORANGE),
            ]
        )
        printWithColor(
            f"<<<------------------------------------------------------------------------->>>\n",
            Color.BLUE,
        )
        return listener.module.ident_uniq_name
