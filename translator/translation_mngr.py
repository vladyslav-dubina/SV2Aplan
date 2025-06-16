from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker

from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from AppModule.app.translator.base_translator_mngr import BaseTranslationManager
from AppModule.app.program.program import Program
from AppModule.app.classes.module_call import ModuleCall


class TranslationManager(BaseTranslationManager):
    def setup(self, data):
        self.logger.info("Set up translator environment \n", color="bold_yellow")
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def translate(self, module_call: ModuleCall | None = None):
        from listener.listener import SVToAplanListener

        self.logger.info("Translation process start...", color="bold_yellow")

        listener: SVToAplanListener = SVToAplanListener(module_call)
        self.walker.walk(listener, self.tree)
        program = Program()
        self.logger.info(f"File tranlation process finished!", color="bold_yellow")
        self.logger.info( f"File {program.file_path}  tranlation process finished!", color="bold_purple"
        )
        self.logger.delimetr(color="blue")
        return listener.module.ident_uniq_name
