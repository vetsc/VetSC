SSA_TYPE_FUNCTION = "function"
SSA_TYPE_CONSTANT = "constant"


class SSA(object):
    '''TODO'''

    def __init__(self, new_assignement=None, method_name=None, args=None, instr_type=SSA_TYPE_FUNCTION):
        """ TODO """
        self.new_assignement = new_assignement
        self.method_name = method_name
        self.args = args
        self.instr_type = instr_type
        

        # Yue: store the original instruction of this ssa
        self.instr = None
        # Yue: store the variable object it defines
        self.defVar = None
        # Yue: store the variables used in this SSA
        self.useVars = list()
        # Yue: store implicit dataflow. 
        # element in this list means this SSA has data dependency with self
        self.implicitUsages = list()
        self.implicitDefs = list()


    def addImplicitUsages(self, ssa):
        self.implicitUsages.append(ssa)


    def getImplicitUsages(self):
        return self.implicitUsages


    def addImplicitDefs(self, ssa):
        self.implicitDefs.append(ssa)


    def getImplicitDefs(self):
        return self.implicitDefs


    # Yue: set the variable it defines
    def setDefVar(self, defVar):
        self.defVar = defVar


    def addUseVar(self, useVar):
        self.useVars.append(useVar)


    def getUseVars(self):
        return self.useVars


    def getDefVar(self):
        return self.defVar

    
    def setInst(self, inst):
        self.instr = inst
    
    def getInst(self):
        return self.instr


    

    def changeArgWithVar(self, arg, var):
        if arg in self.useVars:
            self.useVars.remove(arg)
            self.useVars.append(var)
        return

    

    def detail(self):
        out = ''
        out += 'new_assignement = ' + str(self.new_assignement) + '\n'
        out += 'method_name = ' + str(self.method_name) + '\n'
        out += 'args = ' + str(self.args) + '\n'
        out += 'instr_type = ' + str(self.instr_type) + '\n'
        if self.defVar != None:
            out += 'def variable = ' + self.defVar.name + '\n'  
        out += '\n\n'
        return out

    def format(self):
        out = ''
        if self.is_constant:
            if self.new_assignement != None:
                out += '%{:02X}'.format(self.new_assignement)
                out += ' = '
            if self.args != None:
                out += 'arg constant: #0x%X' % self.args
        elif self.is_function:
            if self.new_assignement != None:
                out += '%{:02X}'.format(self.new_assignement)
                out += ' = '
            if self.method_name:
                out += '%s(' % self.method_name
            if self.args != None:
                out += ', '.join('arg: %{:02X}'.format(arg.ssa.new_assignement) for arg in self.args)
            out += ')'
        else:
            raise Exception('ssa_format no instr_type ')
        return out


    def normalized_format(self):
        out = ''
        if self.is_constant:
            if self.new_assignement != None:
                out += 'var = '
            if self.args != None:
                out += 'arg constant: #0x%X' % self.args
        elif self.is_function:
            if self.new_assignement != None:
                out += 'var = '
            if self.method_name:
                out += '%s(' % self.method_name
            out += ')'
        else:
            raise Exception('ssa_format no instr_type ')
        return out








    @property
    def is_constant(self):
        """ TODO """
        return self.instr_type == SSA_TYPE_CONSTANT

    @property
    def is_function(self):
        """ TODO """
        return self.instr_type == SSA_TYPE_FUNCTION
