from antlr4_verilog import InputStream, CommonTokenStream, ParseTreeWalker
from antlr4_verilog.verilog import VerilogLexer, VerilogParser, VerilogParserListener
from antlr4_verilog.systemverilog import SystemVerilogLexer, SystemVerilogParser, SystemVerilogParserListener
from structures.module_params import Parametr
from io import StringIO


class SV2aplan():
    def __init__(self, input_port_ident, output_port_ident, internal_signals, identifier, assignment_counter, if_counter):
        self.identifier = identifier
        self.input_port_ident = input_port_ident
        self.output_port_ident = output_port_ident
        self.internal_signals = internal_signals
        self.assignment_counter = assignment_counter
        self.if_counter = if_counter
        self.identifierUpper = self.identifier.upper()
        self.identifierLower = self.identifier.lower()
        self.subsiquence = []

    def addCommaAndNeLines(self, input):
        if (len(input) > 0):
            input = ',\n\n' + input
        return input

    def findAndChangeNamesToAplanNames(self, input: str):
        for elem in self.internal_signals:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))

        for elem in self.input_port_ident:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))

        for elem in self.output_port_ident:
            input = input.replace(
                elem, '{0}.{1}'.format(self.identifier, elem))
        return input

    def Sensetive2Aplan(self, alwaysStrBody):
        sens_list = []
        for elem in self.input_port_ident:
            if (alwaysStrBody.find(elem) != -1):
                sens_list.append(elem)
        change_call = 'Sensitive'
        self.subsiquence.append(
            'Sensitive')
        return [change_call, sens_list]

    def sv2aplan(self, ctx):
        subsiquence = []
        action = ''
        beh = ''
        if ctx.getChildCount() == 0:
            return ['', '', []]
        for child in ctx.getChildren():
            if (type(child) is SystemVerilogParser.Variable_decl_assignmentContext):
                assign = child.getText()
                assignWithReplacedNames = self.findAndChangeNamesToAplanNames(
                    assign)
                act = ''
                act += 'assign{0} = (\n\t\t(1)->\n'.format(self.assignment_counter)
                act += '\t\t("{2}#{3}:action \'{0}\';")\n\t\t({1})'.format(assign,
                                                                           assignWithReplacedNames, self.identifierUpper, self.identifierLower)
                act += '),\n\n'
                action += act
                subsiquence.append(
                    'assign{0}'.format(self.assignment_counter))
                beh += '.assign{0}'.format(self.assignment_counter)
                self.assignment_counter += 1
            elif (type(child) is SystemVerilogParser.Conditional_statementContext):
                predicate = child.cond_predicate()
                for elem in predicate:
                    predicateString = elem.getText()
                    if (len(predicateString) > 0):
                        predicateWithReplacedNames = self.findAndChangeNamesToAplanNames(
                            predicateString)
                        action += '''if{0} = (
        ({1})->
        ("{2}#{3}:action 'if ({4})';")
        (1)),\n\n'''.format(self.if_counter, predicateWithReplacedNames, self.identifierUpper, self.identifierLower, predicateString)

                statements = child.statement_or_null()
                subsiquence = []
                for elemid in range(len(statements)):
                    res = self.sv2aplan(statements[elemid])
                    action += res[0]
                    reverseSubs = res[2][::-1]
                    subsLen = len(res[2])
                    if (subsLen > 0):
                        if (elemid > 0):
                            beh += 'BODY_ELSE_IF{0} = '.format(self.if_counter)
                            subsiquence.append(
                                'BODY_ELSE_IF{0}'.format(self.if_counter))
                        else:
                            beh += 'BODY_IF{0} = '.format(self.if_counter)
                            subsiquence.append(
                                'BODY_IF{0}'.format(self.if_counter))
                        for subsIndex in range(subsLen):
                            if (subsIndex == 0):
                                beh += 'Sensitive(' + \
                                    reverseSubs[subsIndex] + ')'
                            else:
                                beh += reverseSubs[subsIndex]
                            if (subsIndex + 1 == subsLen):
                                beh += ',\n'
                            else:
                                beh += '.'
                if (len(subsiquence) > 0):
                    beh = 'if{0}.{1} + !if{0}.{2},\n'.format(
                        self.if_counter, subsiquence[0], subsiquence[1]) + beh
                    subsiquence = []
                self.if_counter += 1
            else:
                res = self.sv2aplan(child)
                if (len(res[1]) > 1):
                    tmp = res[1].split('.')
                    if (len(tmp) == 2):
                        res[1] = 'Sensetive(' + tmp[1] + ')'
                    beh += res[1]
                    action += res[0]
                    subsiquence = res[2] + subsiquence

        return [action, beh, subsiquence]


class ModuleAnalyzeListener(SystemVerilogParserListener):
    def __init__(self):
        self.identifier = ''
        self.params = []
        self.input_port_ident = []
        self.output_port_ident = []
        self.internal_signals = []
        self.assignments = []
        self.assignment_counter = 1
        self.inp_sensetive_list = []
        self.if_counter = 1
        self.actions = ''
        self.behaviour = ''
        self.alwaysCounter = 1
        self.not_blocked_prot = []
        self.parameters = []

    def enterModule_declaration(self, ctx):
        self.identifier = ctx.module_ansi_header().module_identifier().getText()

    def exitNet_declaration(self, ctx):
        if (ctx.net_type().getText() == 'wire'):
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                self.internal_signals.append(identifier)
                expression = elem.expression().getText()
                if (expression):
                    self.assignments.append([identifier, expression])
                    assign = elem.getText()
                    sv2aplan = SV2aplan(self.input_port_ident, self.output_port_ident,
                                        self.internal_signals, self.identifier, self.assignment_counter, self.if_counter)
                    assignWithReplacedNames = sv2aplan.findAndChangeNamesToAplanNames(
                        assign)
                    act = 'assign{0} = (\n\t\t(1)->\n'.format(self.assignment_counter)
                    act += '\t\t("{2}#{3}:action \'{0}\';")\n\t\t({1})'.format(assign,
                                                                               assignWithReplacedNames, sv2aplan.identifierUpper, sv2aplan.identifierLower)
                    act += '),\n\n'
                    self.actions += act
                    self.not_blocked_prot.append(
                        'assign{0}'.format(self.assignment_counter))
                    self.assignment_counter += 1

    def exitAnsi_port_declaration(self, ctx):
        if (ctx.net_port_header().getText() == 'input'):
            self.input_port_ident.append(ctx.port_identifier().getText())
        if (ctx.net_port_header().getText() == 'output'):
            self.output_port_ident.append(
                ctx.port_identifier().getText())

    def exitParam_assignment(self, ctx):
        self.params.append(Parametr(ctx.parameter_identifier(
        ).getText(), ctx.constant_param_expression().getText()))

    def enterAlways_construct(self, ctx):
        sv2aplan = SV2aplan(self.input_port_ident, self.output_port_ident,
                            self.internal_signals, self.identifier, self.assignment_counter, self.if_counter)
        sv2aplanResult = sv2aplan.sv2aplan(ctx)

        self.actions += sv2aplanResult[0]
        if (sv2aplanResult[1].find('.') == 0):
            sv2aplanResult[1] = sv2aplanResult[1][1:]
        sensetive = sv2aplan.Sensetive2Aplan(ctx.getText())
        if (len(sensetive[0]) > 0):
            if (len(self.behaviour) > 0):
                self.behaviour += ',\n'
            changeBeh = 'B{0} = ALWAYS_{0}'.format(
                self.alwaysCounter)
            self.behaviour += changeBeh

        if (len(self.behaviour) > 0):
            self.behaviour += ',\n'
            self.behaviour += 'ALWAYS_{0} = '.format(
                self.alwaysCounter) + sv2aplanResult[1]
        else:
            self.behaviour = 'ALWAYS_{0} = '.format(
                self.alwaysCounter) + sv2aplanResult[1]

        beh_sensetive = 'B{0}, '.format(self.alwaysCounter)
        for index, element in enumerate(sensetive[1]):
            beh_sensetive += 'code.' + element
            if (index + 1 < len(sensetive[1])):
                beh_sensetive += ' || '
        self.inp_sensetive_list.append(beh_sensetive)
        self.assignment_counter = sv2aplan.assignment_counter
        self.if_counter = sv2aplan.if_counter
        self.alwaysCounter += 1


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
        beh_counter = 0
        beh_counter += listener.alwaysCounter
        return [listener.identifier, listener.params, listener.input_port_ident, listener.output_port_ident, listener.internal_signals, listener.not_blocked_prot, listener.identifier, listener.actions, listener.behaviour, listener.inp_sensetive_list, beh_counter, listener.parameters]
