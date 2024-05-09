from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from listener.system_verilog_listener import SVListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from utils import printWithColor, Color

class SystemVerilogFind():
    def setUp(self, data):
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def startTranslate(self):
        printWithColor('Tranlation process start... \n', Color.ORANGE)

        listener = SVListener()
        self.walker.walk(listener, self.tree)
        printWithColor('Tranlation process finished! \n', Color.ORANGE)
        beh_counter = 0
        beh_counter += listener.always_counter
        return [listener.identifier, listener.params, listener.input_port_ident, listener.output_port_ident, listener.internal_signals, listener.not_blocked_prot, listener.identifier, listener.actions, listener.behaviour, listener.inp_sensetive_list, beh_counter, listener.parameters]
