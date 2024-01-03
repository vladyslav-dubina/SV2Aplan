from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4_verilog.verilog import VerilogLexer, VerilogParser, VerilogParserListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser, SystemVerilogParserListener
from structures.module_params import Parametr
from io import StringIO


class SV2aplan():
    def __init__(self, inputPortIdent, outputPortIdent, internalSignals, identifier, assignment_counter, change_counter):
        self.identifier = identifier
        self.inputPortIdent = inputPortIdent
        self.outputPortIdent = outputPortIdent
        self.internalSignals = internalSignals
        self.assignment_counter = assignment_counter
        self.change_counter = change_counter
        self.identifierUpper = self.identifier.upper()
        self.identifierLower = self.identifier.lower()

    def addCommaAndNeLines(self, input):
        if (len(input) > 0):
            input += ',\n\n'
        else:
            input += '\n\n'
        return input

    def findAndChangeNamesToAplanNames(self, input: str):
        for elem in self.internalSignals:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))

        for elem in self.inputPortIdent:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))

        for elem in self.outputPortIdent:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))
        return input

    def Sensetive2Aplan(self, alwaysStrBody):
        sens_list = []
        result = ''
        for elem in self.inputPortIdent:
            if (alwaysStrBody.find(elem) != -1):
                sens_list.append(elem)
        identifierUpper = self.identifier.upper()
        params = ''
        condition = ''
        for i in range(len(sens_list)):
            params += 'x{0}'.format(i)
            condition += '{0}.sensitive(x{1}) == 1'.format(
                self.identifierLower, i)
            if (i < len(sens_list) - 1):
                params += ', '
                condition += ' || '
        change = '''change_{0}({3}) = (
		({4})->
		("{1}#{2}:action 'show=0';")
		(1)),'''.format(self.change_counter, self.identifierUpper, self.identifierLower, params, condition)
        return [sens_list, change]

    def sv2aplan(self, ctx):
        result = ''
        if ctx.getChildCount() == 0:
            return ''
        for child in ctx.getChildren():
            if (type(child) is SystemVerilogParser.Variable_decl_assignmentContext):
                assign = child.getText()
                assignWithReplacedNames = self.findAndChangeNamesToAplanNames(
                    assign)
                result = self.addCommaAndNeLines(result)
                act = ''
                act += 'assign{0} = (\n\t\t(1)->\n'.format(self.assignment_counter)
                act += '\t\t("{2}#{3}:action \'{0}\';")\n\t\t({1})'.format(assign,
                                                                           assignWithReplacedNames, self.identifierUpper, self.identifierLower)
                act += ')'
                result += act
                self.assignment_counter += 1
            else:
                result += self.sv2aplan(child)
        return result


class ModuleAnalyzeListener(SystemVerilogParserListener):
    def __init__(self):
        self.identifier = ''
        self.params = []
        self.inputPortIdent = []
        self.outputPortIdent = []
        self.internalSignals = []
        self.assignments = []
        self.assignment_counter = 1
        self.change_counter = 1

    def enterModule_declaration(self, ctx):
        self.identifier = ctx.module_ansi_header().module_identifier().getText()

    # def exitParameter_port_declaration(self, ctx):
    #    assignList = ctx.parameter_declaration(
    #    ).list_of_param_assignments().param_assignment()
    #    for elem in assignList:
    #        self.params.append(Parametr(elem.parameter_identifier(
    #       ).getText(), elem.constant_param_expression().getText()))
    def exitNet_declaration(self, ctx):
        if (ctx.net_type().getText() == 'wire'):
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                self.internalSignals.append(identifier)
                expression = elem.expression().getText()
                if (expression):
                    self.assignments.append([identifier, expression])

    def exitAnsi_port_declaration(self, ctx):
        if (ctx.net_port_header().getText() == 'input'):
            self.inputPortIdent.append(ctx.port_identifier().getText())
        if (ctx.net_port_header().getText() == 'output'):
            self.outputPortIdent.append(
                ctx.port_identifier().getText())

    def exitParam_assignment(self, ctx):
        self.params.append(Parametr(ctx.parameter_identifier(
        ).getText(), ctx.constant_param_expression().getText()))

    def enterAlways_construct(self, ctx):
        print("------------------")
        sv2aplan = SV2aplan(self.inputPortIdent, self.outputPortIdent,
                            self.internalSignals, self.identifier, self.assignment_counter, self.change_counter)
        print(sv2aplan.sv2aplan(ctx))
        print(sv2aplan.Sensetive2Aplan(ctx.getText()))
        self.assignment_counter = sv2aplan.assignment_counter
        self.change_counter = sv2aplan.change_counter
       # print(ctx.start.line)

    def enterConditional_statement(self, ctx):
        print("++++++++++++++++++")
        print(ctx.getText())
        print(ctx.start.line)

    def exitVariable_decl_assignment(self, ctx):
        # dimention = ctx.variable_dimension()
        # if (len(dimention) > 0):
        #   dimention = dimention[0].getText()
       # print('===========')
       # print(ctx.start.line)
        identifier = ctx.variable_identifier().getText()
        if (ctx.expression()):
            expression = ctx.expression().getText()
            self.assignments.append([identifier, expression])

    # body of module
    # def exitModule_common_item(self, ctx):
      #  print('++++++++++')
       # print(ctx.getText())


class SystemVerilogFind():
    def setUp(self, data):
        lexer = SystemVerilogLexer(InputStream(data))
        stream = CommonTokenStream(lexer)
        parser = SystemVerilogParser(stream)
        self.tree = parser.source_text()
        self.walker = ParseTreeWalker()

    def walkerFunk(self):
        class Listener(SystemVerilogParserListener):
            def exitLibrary_text(self, ctx):
                print(ctx.getText())
        listener = Listener()
        self.walker.walk(listener, self.tree)

    def start_analyze(self):
        print('Analyze started')

        listener = ModuleAnalyzeListener()
        self.walker.walk(listener, self.tree)
        print('Analyze finished')
        return [listener.identifier, listener.params, listener.inputPortIdent, listener.outputPortIdent, listener.internalSignals, listener.assignments, listener.identifier]

    def test_module_inputs(self):
        class ModuleInputListener(SystemVerilogParserListener):
            def __init__(self):
                self.declarations = []

            def exitInput_declaration(self, ctx):
                print(ctx)

            def exitInput_identifier(self, ctx):
                print("tetra")
                print(ctx)

        listener = ModuleInputListener()
        self.walker.walk(listener, self.tree)
        print(listener.declarations)

    def test_variable_assignment(self):
        class VariableAssignmentListener(SystemVerilogParserListener):
            def __init__(self):
                self.vars = []
                self.opVars = []
                self.decl = []

            def exitVariable_decl_assignment(self, ctx):
                print(ctx.depth())
                dimention = ctx.variable_dimension()
                if (len(dimention) > 0):
                    dimention = dimention[0].getText()
                self.identifier = ctx.variable_identifier().getText()
                if (ctx.expression()):
                    self.expression = ctx.expression().getText()
                    self.vars.append(
                        [self.identifier, dimention, self.expression])
                else:
                    self.decl.append(self.identifier)

        listener = VariableAssignmentListener()
        self.walker.walk(listener, self.tree)
        print(listener.vars)
        print("---------------")
        print(listener.opVars)
        print("---------------")
        print(listener.decl)
