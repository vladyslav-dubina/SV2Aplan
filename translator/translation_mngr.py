from pathlib import Path
from antlr4 import FileStream
from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker

from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser
from Core.src.translator.base_translator_mngr import BaseTranslationManager
from Core.src.program.program import Program
from Core.src.classes.design_unit_call import DesignUnitCall


class TranslationManager(BaseTranslationManager):
    def setup(self, file_path: Path):
        self.logger.delimetr(color="blue", text=f"Read file {file_path}")
        self.logger.info("Set up translator environment \n", color="bold_yellow")
        lexer = SystemVerilogLexer(FileStream(file_path))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()
        self.program = Program()
        self.program.file_path = file_path

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
