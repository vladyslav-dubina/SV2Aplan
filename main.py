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
        self.assignments = []
        self.identifier = ''

        self.inputsFlag = False
        self.outputFlag = False
        self.internalFlag = False
        self.assignmentsFlag = False
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
        self.assignments = input[5]
        self.identifier = input[6]
        if (len(self.moduleInputs) > 0):
            self.inputsFlag = True

        if (len(self.moduleOutputs) > 0):
            self.outputFlag = True

        if (len(self.internalSignals) > 0):
            self.internalFlag = True

        if (len(self.assignments) > 0):
            self.assignmentsFlag = True

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
                env += '{0},'.format(elem)
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
        # Assing
        # ----------------------------------
        act = ''
        if (self.assignmentsFlag):
            for i in range(len(self.assignments)):
                act += 'assign{0} = (\n\t\t(1)->\n'.format(i+1)
                act += '\t\t("CODE#code:action \'{0} = {1}\';")\n\t\t(code.{0} = {1})'.format(self.assignments[i][0], self.assignments[i][1])
                if (i+1 < len(self.assignments)):
                    act += '),\n\n'
                else:
                    act += ')\n\n'
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
    ))'''.format(identifierUpper, identifierUpper.lower())
        self.writeToFile('results/project.act', act)

    def createAplan(self):
        self.createEVT()
        self.createENV()
        self.createAction()

    def __str__(self):
        return "Identifier: {0}\nParametrs:\n{1}\nInput ports: \n {2}\nOutput ports: \n {3}\nAssignments: \n {4}".format(self.moduleIdentifier,
                                                                                                                         self.paramsPrint(),
                                                                                                                         self.printArray(
                                                                                                                             self.moduleInputs, False),
                                                                                                                         self.printArray(
                                                                                                                             self.moduleOutputs, False),
                                                                                                                         self.printArray(
                                                                                                                             self.assignments, True)
                                                                                                                         )


program = Program()
program.setUp("example.sv")
analyze_result = program.finder.start_analyze()
program.setData(analyze_result)
print(program)
program.createAplan()
