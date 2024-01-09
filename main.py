from structures.module_params import Parametr
from analyzer import SystemVerilogFind
import os


class Program():
    def __init__(self) -> None:
        self.moduleIdentifier = ''
        self.moduleParametrs = []
        self.moduleInputs = []
        self.moduleOutputs = []
        self.internalSignals = []
        self.notBlockedProt = []
        self.behaviour = ''
        self.actions = ''
        self.identifier = ''
        self.changeCounter = 0
        self.behCounter = 0
        self.parameters = []

        self.inputsFlag = False
        self.outputFlag = False
        self.internalFlag = False
        self.finder = SystemVerilogFind()

    def setUp(self, path):
        print('Set up env')
        f = open(path, "r")
        data = f.read()
        f.close()
        self.finder.setUp(data)
        self.createResDir()

    def setData(self, input):
        self.moduleIdentifier = input[0]
        self.moduleParametrs = input[1]
        self.moduleInputs = input[2]
        self.moduleOutputs = input[3]
        self.internalSignals = input[4]
        self.notBlockedProt = input[5]
        self.identifier = input[6]
        self.actions = input[7]
        self.behaviour = input[8]
        self.changeCounter = input[9]
        self.behCounter = input[10]
        self.parameters = input[11]

        if (len(self.moduleInputs) > 0):
            self.inputsFlag = True

        if (len(self.moduleOutputs) > 0):
            self.outputFlag = True

        if (len(self.internalSignals) > 0):
            self.internalFlag = True

    def paramsPrint(self):
        result = ''
        for elem in self.moduleParametrs:
            result += '\t' + elem.__str__() + '\n'
        return result

    def printArray(self, array, assignmentFlag):
        result = ''
        for elem in array:
            if (assignmentFlag):
                result += '\t{0} = {1}\n'.format(elem[0], elem[1])
            else:
                result += '\t{0}\n'.format(elem)
        return result

    def createResDir(self):
        if (not os.path.exists('results')):
            os.mkdir('results')

    def writeToFile(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def createEVT(self):
        evt = 'events(\n'
        for elem in self.moduleInputs:
            evt += '\ts_{0}:obj(x1:Bits 64);\n'.format(elem)
        evt += ');'
        self.writeToFile('results/project.evt_descript', evt)

    def createENV(self):
        env = 'environment (\n'  # Open env

        # ----------------------------------
        # Types
        # ----------------------------------
        env += '\ttypes : obj (\n'
        if (self.inputsFlag):
            env += '\t\tinputSignals : ('
            for elem in self.moduleInputs:
                env += '_{0},'.format(elem)
            env += ')\n'
        if (self.internalFlag):
            env += '\t\tinternalSignals : ('
            for elem in self.internalSignals:
                env += '{0},'.format(elem)
            env += ')\n'
        env += '\t);\n'

        # ----------------------------------
        # Attributes
        # ----------------------------------

        env += '\tattributes : obj (\n'
        env += '\t\tNil\n'
        env += '\t);\n'

        # ----------------------------------
        # Agents types
        # ----------------------------------

        env += '\tagent_types : obj (\n'

        if (self.inputsFlag or self.outputFlag or self.internalFlag):
            env += '\t\t{0} : obj (\n'.format(self.identifier.upper())

            for elem in self.internalSignals:
                env += '\t\t\t{0}:Bits 64,\n'.format(elem)

            for elem in self.moduleInputs:
                env += '\t\t\t{0}:Bits 64,\n'.format(elem)

            for elem in self.moduleOutputs:
                env += '\t\t\t{0}:Bits 64,\n'.format(elem)

            env += '\t\t\tsensitive:(inputSignals)->bool,\n'
            env += '\t\t\tchange:(internalSignals)->bool,\n'
            env += '\t\t)\n'

        env += '\t);\n'

        # ----------------------------------
        # Agents
        # ----------------------------------
        env += '\tagents : obj (\n'
        if (self.inputsFlag or self.outputFlag or self.internalFlag):
            env += '\t\t{0} : obj (code)\n'.format(self.identifier.upper())
        env += '\t\tENVIRONMENT : obj (env)\n'
        env += '\t);\n'

        # ----------------------------------
        # Axioms
        # ----------------------------------
        env += '\taxioms : obj (Nil);\n'

        # ----------------------------------
        # Logic formula
        # ----------------------------------
        env += '\tlogic_formula : obj (\n'
        if (self.inputsFlag):
            env += '\t\tForall  (e :  inputSignals)( code.sensitive(e) ==  0)'
            env += ' && \n' if self.internalFlag else '\n'
        if (self.internalFlag):
            env += '\t\tForall  (e :  internalSignals)( code.change(e) ==  0)\n'
        env += '\t)\n'
        env += ');'  # Close env

        self.writeToFile('results/project.env_descript', env)

    def createAction(self):
        # ----------------------------------
        # Actions
        # ----------------------------------
        act = ''
        identifierUpper = self.identifier.upper()
        act += '''receive(x,y,z) = (Exist (p:Bits  64)(
        (1)->
        ("ENV#env:out z,1 (p) to {0}#{1};")
        ({1}.y = p; {1}.sensitive(x) =  1)
    )),

reset_change = (Forall (e:internalSignals)(
        (1)->
        ("{0}#{1}:action 'show=0';")
        ({1}.change(e) = 0)
    )),

reset_sensetive = (Forall (e:inputSignals)(
        (1)->
        ("{0}#{1}:action 'show=0';")
        ({1}.sensitive(e) = 0)
    )),\n\n'''.format(identifierUpper, identifierUpper.lower())
        act += self.actions
        remove_index = act.rfind(',')
        act = act[:remove_index] + act[remove_index+1:]
        self.writeToFile('results/project.act', act)

    def createBeh(self):
        # ----------------------------------
        # Behaviour
        # ----------------------------------
        beh = self.behaviour
        inp = 'INP = '
        for i in range(len(self.moduleInputs)):
            inp += 'receive(_{0}, {0}, s_{0})'.format(self.moduleInputs[i])
            if (i+1 == len(self.moduleInputs)):
                inp += ',\n'
            else:
                inp += ' +\n\t\t'
        beh = inp + beh
        beh_part2 = ''
        for i in range(self.behCounter - 1):
            beh_part2 += 'B{0}'.format(i+1)
            if (i+1 < self.behCounter - 1):
                beh_part2 += ' || '

        if (len(beh_part2) > 0):
            beh_part2 = '{ ' + beh_part2 + ' }'

        beh_part1 = ''
        self.notBlockedProt = self.notBlockedProt[::-1]
        for i in range(len(self.notBlockedProt)):
            beh_part1 += self.notBlockedProt[i]
            if (i+1 != len(self.notBlockedProt)):
                beh_part2 += '.'
        beh = 'B0 = ({0}.INP; {1}; reset_sensetive; reset_change; B0),\n'.format(
            beh_part1, beh_part2) + beh
        remove_index = beh.rfind(',')
        beh = beh[:remove_index] + beh[remove_index+1:]
        self.parameters = list(dict.fromkeys(self.parameters))
        params_str = ''
        for i in range(len(self.parameters)):
            params_str += self.parameters[i]
            if (i+1 != len(self.parameters)):
                params_str += ', '
        beh = 'rs({0}) (\n'.format(params_str) + beh + ')'
        self.writeToFile('results/project.behp', beh)

    def createAplan(self):
        self.createEVT()
        self.createENV()
        self.createAction()
        self.createBeh()


program = Program()
program.setUp("example.sv")
analyze_result = program.finder.start_analyze()
program.setData(analyze_result)
program.createAplan()
