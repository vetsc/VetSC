# This class defines VARIABLE that stores the variable information, including
# variable name (string)
# block that defines it (block name)
# instruction that defines it (instruction object)
# Since we are dealing with SSA format, there could be only one definition for each variable

class Variable(object):
    '''TODO'''

    def __init__(self, name, defBlock, defINsn):
        """ TODO """
        self.name = name
        self.defBlock = defBlock
        self.defInsn = defINsn

        self.useBlocks = list()
        self.useInsns = list()

    def getDefBlock(self):
        return self.defBlock

    
    def getDefInsn(self):
        return self.defInsn


    def addUseBlocks(self, block):
        if block not in self.useBlocks:
            self.useBlocks.append(block)

    
    def addUseInsns(self, instruction):
        if instruction not in self.useInsns:
            self.useInsns.append(instruction)


    def getUseBlocks(self):
        return self.useBlocks

    def getUseInsns(self):
        return self.useInsns



    def __str__(self):
        out = '\n\t==============================================================\n'
        out += '\tVariable name: ' + str(self.name) + '\n\n'
        # out += '\tdefined in Block: ' + str(self.defBlock) + '\n'
        out += '\tdefined in SSA instruction: ' + str(self.defInsn.ssa.format()) + '\n'
        # out += 'used in Blocks: '
        # for b in self.useBlocks:
        #     out += str(b)
        
        out += '\tused in Insns: '
        for i in self.useInsns:
            out += '\t\t' + str(i.ssa.format())
            
        out += '\n\t============================================================\n\n'
        return out


