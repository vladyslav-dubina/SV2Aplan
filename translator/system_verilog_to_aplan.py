from antlr4_verilog.systemverilog import SystemVerilogParser

#


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

    def sensetive2Aplan(self, alwaysStrBody):
        sens_list = []
        for elem in self.input_port_ident:
            if (alwaysStrBody.find(elem) != -1):
                sens_list.append(elem)
        change_call = 'Sensitive'
        self.subsiquence.append(
            'Sensitive')
        return [change_call, sens_list]

    def body2Aplan(self, ctx):
        subsiquence = []
        action = ''
        beh = ''
        if ctx.getChildCount() == 0:
            return ['', '', []]
        for child in ctx.getChildren():
            if (type(child) is SystemVerilogParser.Variable_decl_assignmentContext):
                assign = child.getText()
                assign_with_replaced_names = self.findAndChangeNamesToAplanNames(
                    assign)
                act = ''
                act += 'assign{0} = (\n\t\t(1)->\n'.format(self.assignment_counter)
                act += '\t\t("{2}#{3}:action \'{0}\';")\n\t\t({1})'.format(assign,
                                                                           assign_with_replaced_names, self.identifierUpper, self.identifierLower)
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
                    res = self.body2Aplan(statements[elemid])
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
                res = self.body2Aplan(child)
                if (len(res[1]) > 1):
                    tmp = res[1].split('.')
                    if (len(tmp) == 2):
                        res[1] = 'Sensetive(' + tmp[1] + ')'
                    beh += res[1]
                    action += res[0]
                    subsiquence = res[2] + subsiquence

        return [action, beh, subsiquence]

    def always2Aplan(self, ctx, always_counter):
        behaviour = ''

        sv_to_aplan_result = self.body2Aplan(ctx)
        actions = sv_to_aplan_result[0]

        if (sv_to_aplan_result[1].find('.') == 0):
            sv_to_aplan_result[1] = sv_to_aplan_result[1][1:]

        sensetive = self.sensetive2Aplan(ctx.getText())
        if (len(sensetive[0]) > 0):
            if (len(behaviour) > 0):
                behaviour += ',\n'
            sensetive_beh = 'B{0} = ALWAYS_{0}'.format(
                always_counter)
            behaviour += sensetive_beh

        if (len(behaviour) > 0):
            behaviour += ',\n'
            behaviour += 'ALWAYS_{0} = '.format(
                always_counter) + sv_to_aplan_result[1]
        else:
            behaviour = 'ALWAYS_{0} = '.format(
                always_counter) + sv_to_aplan_result[1]

        beh_sensetive = 'B{0}, '.format(always_counter)
        for index, element in enumerate(sensetive[1]):
            beh_sensetive += 'code.' + element
            if (index + 1 < len(sensetive[1])):
                beh_sensetive += ' || '

        return [actions, behaviour, beh_sensetive, self.assignment_counter, self.if_counter]

    def declaration2Aplan(self, ctx):
        assign_sv = ctx.getText()
        assign_with_replaced_names = self.findAndChangeNamesToAplanNames(
            assign_sv)
        action = 'assign{0} = (\n\t\t(1)->\n'.format(self.assignment_counter)
        action += '\t\t("{2}#{3}:action \'{0}\';")\n\t\t({1})'.format(assign_sv,
                                                                      assign_with_replaced_names, self.identifierUpper, self.identifierLower)
        action += '),\n\n'
        not_blocked_prot = 'assign{0}'.format(self.assignment_counter)
        return [action, not_blocked_prot]
