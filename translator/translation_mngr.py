from antlr4 import FileStream
from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker

from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from AppModule.app.translator.base_translator_mngr import BaseTranslationManager
from AppModule.app.program.program import Program
from AppModule.app.classes.design_unit_call import DesignUnitCall


class TranslationManager(BaseTranslationManager):
    program = Program()

    def setup(self, file_name):
        self.program.file_path = file_name
        self.logger.delimetr(color="blue", text=f"Read file {file_name}")
        self.logger.info("Set up translator environment \n", color="bold_yellow")
        lexer = SystemVerilogLexer(FileStream(file_name))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def translate(self, design_unit_call: DesignUnitCall | None = None):
        from listener.listener import SVToAplanListener

        self.logger.info("Translation process start...", color="bold_yellow")

        listener: SVToAplanListener = SVToAplanListener(design_unit_call)
        self.walker.walk(listener, self.tree)

        self.logger.info(f"File tranlation process finished!", color="bold_yellow")
        self.logger.info(
            f"File {self.program.file_path}  tranlation process finished!",
            color="bold_purple",
        )
        self.logger.delimetr(color="blue")
        return listener.design_unit.ident_uniq_name
