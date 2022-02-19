from octopus.analysis.cfg import CFG
from octopus.analysis.graph import CFGGraph
from octopus.core.function import Function
from octopus.core.basicblock import BasicBlock
from octopus.core.variable import Variable
from octopus.core.ssa import SSA

from octopus.arch.evm.disassembler import EvmDisassembler

from octopus.arch.evm.cfg import EvmCFG

import json
import os
import copy

from logging import getLogger
logging = getLogger(__name__)

dataflow_log_enabled = False

SPECIAL_VARIABLES = ["CALLVALUE", "CALLER", "NUMBER", "TIMESTAMP", "BALANCE", "ORIGIN", "ADDRESS", "BLOCKHASH", "COINBASE", "DIFFICULTY", "GASLIMIT", "GASPRICE"]


# we are trying to do a simple storage model by recording all the offsets as well as their semantic meanings
storage_model = {}




class Model: 
    def __init__(self, bytecode_hex):
        self.cfg = EvmCFG(bytecode_hex)

        # Yue: stores all the SSA format variables
        self.variables = list()

        # Yue: store var with concrete values for optimization
        self.concrete_vars = list()

        # Yue: stores all the vars whose value comes from a special variable such as CALLVALUE
        self.specialVars = {}



    # Yue: print the blocks and their instructions in SSA format
    def printBlocks(self):
        for i in self.cfg.basicblocks:
            # if i.function_name != "buy(address)":
            #     continue

            print("basic block: \n" + str(i) + "\n")
            for j in i.instructions:
                print("\nINSTRUCTION:\n")
                if j.ssa != None:
                    # print("instruction in detail: " + j.ssa.detail())
                    print("instruction in format: " + j.ssa.format() + "\n\n")


    # Yue: collect all the variable names
    def collectAllVariables(self):
        # self.printBlocks()
        for i in self.cfg.basicblocks:
            for j in i.instructions:
                j.basic_block = i

                if j.ssa != None:
                    j.ssa.setInst(j)

                if j.ssa != None and j.ssa.new_assignement != None:
                    var = Variable('%{:02X}'.format(j.ssa.new_assignement), i, j)
                    self.variables.append(var)
                    if j.ssa.is_constant:
                        self.concrete_vars.append(var)

                    # collect all variables that are the returns of sepcial variable calls such as CALLVALUE()
                    if j.ssa.method_name in SPECIAL_VARIABLES:
                        if j.ssa.method_name not in self.specialVars:
                            varlist = list()
                            self.specialVars[j.ssa.method_name] = varlist
                        self.specialVars[j.ssa.method_name].append(var)

            

    # Yue: return variables whose value come from sepcial variable (e.g., CALLER) in a specific function
    # specialVar: name of the sepcial variable such as "CALLER". If use "*", the function will return all sepcial variables
    # functionName: the function in which the sepcial variable resides
    def retrieveSepcialVar(self, specialVar, funcName):
        if specialVar != "*" and specialVar not in SPECIAL_VARIABLES:
            return None
        
        vars = None
        if specialVar == "*":
            vars = [y for x in self.specialVars.values() for y in x]
        else:
            if specialVar in self.specialVars:
                vars = self.specialVars[specialVar]

        if not vars :
            return None
        
        
        varsInFunc = list()
        for var in vars:
            if funcName in var.defBlock.function_name or funcName == "*":
                varsInFunc.append(var)
        return varsInFunc



    # This function retrieves variables that are defined by the instruction given in a specific function, which can be "*" indicating all functions
    def getDefVarFromFuncs(self, insnName, funcName):
        vars = list()
        for var in self.variables:
            if ((var.getDefInsn().ssa.method_name == insnName)
            and (funcName == "*" or funcName in var.defBlock.function_name)):
                vars.append(var)

        return vars

    # This fuction is the same as retrieveVarsFromFuncs()
    # This function should only be used when an instruction has no def var
    def getInsnsFromFuncs(self, insnName, funcName):
        insns = list()
        for i in self.cfg.basicblocks:
            for j in i.instructions:
                if j.ssa != None:
                    if ((j.ssa.method_name == insnName)
                    and (funcName == "*" or funcName in i.function_name)):
                        insns.append(j)
        return insns



    # Yue: find def-use chain for each variables in SSA format
    def findDefUseChain(self):
        self.collectAllVariables()
        # for every variable, we go through all the instructions to find ones that use it. 
        # TODO: speed up
        # for var in self.variables:
        #     for i in self.cfg.basicblocks:
        #         for j in i.instructions:
        #             if j.ssa == None:
        #                 continue
        #             # fill up the useBlocks and useInsns field of every variable
        #             if j.ssa.is_function and j.ssa.args != None:
        #                 for idx, arg in enumerate(j.ssa.args):
        #                     if var.name == '%{:02X}'.format(arg.ssa.new_assignement):
        #                         # print("FIND use of" + var.name + " in SSA: " + j.ssa.format())
        #                         var.addUseBlocks(i)
        #                         var.addUseInsns(j)
        #                         j.ssa.addUseVar(var)
                    
        #             # fill up the defVar field for every instruction
        #             if (j.ssa != None
        #             and j.ssa.new_assignement != None
        #             and '%{:02X}'.format(j.ssa.new_assignement) == var.name):
        #                 j.ssa.setDefVar(var)
        
        for i in self.cfg.basicblocks:
            prev_instr = None
            for j in i.instructions:
                if prev_instr:
                    prev_instr.next_instr = j
                prev_instr = j

                if j.ssa == None:
                    continue

                

                # fill up the useBlocks and useInsns field of every variable
                if j.ssa.is_function and j.ssa.args != None:
                    for arg in j.ssa.args:
                        for var in self.variables: 
                            if var.name == '%{:02X}'.format(arg.ssa.new_assignement):
                                # print("FIND use of" + var.name + " in SSA: " + j.ssa.format())
                                var.addUseBlocks(i)
                                var.addUseInsns(j)
                                j.ssa.addUseVar(var)
                                continue
                
                for var in self.variables: 
                    # fill up the defVar field for every instruction
                    if (j.ssa.new_assignement != None
                    and '%{:02X}'.format(j.ssa.new_assignement) == var.name):
                        j.ssa.setDefVar(var)
                        continue




    # Yue: perform data flow analysis on a given variable or variable name
    # Return the partial flow graph. 
    # Each node is a ssa format instruction, each edge represents a def-use data flow
    def doForwardDFAForVar(self, var):
        if var == None:
            print("no such variable found for forward dataflow analysis")
            return

        if not isinstance(var, Variable):
            varObj = next((x for x in self.variables if x.name == var), None)
        else:
            varObj = var

        if dataflow_log_enabled:
            print("Found for forward dataflow analysis:", str(varObj))
        
        partialFlowGraph = {}
        visitedInsnSet = list()
        varDef = varObj.getDefInsn().ssa
        visitedInsnSet.append(varDef)
        partialFlowGraph[varDef] = list()
        initInsnSet = list()
        # start from the use insns, see variables defined in them
        for varUse in varObj.getUseInsns():
            if (varUse.ssa not in initInsnSet):
                initInsnSet.append(varUse.ssa)
                partialFlowGraph[varDef].append(varUse.ssa)
        
        while len(initInsnSet) != 0:
            curSsa = initInsnSet.pop()
            visitedInsnSet.append(curSsa)

            if (curSsa.getDefVar() == None 
            and curSsa.getImplicitUsages() == None):
                continue



            if curSsa.getDefVar() != None:
                for i in curSsa.getDefVar().getUseInsns():
                    if ((i.ssa not in initInsnSet)
                    and (i.ssa not in visitedInsnSet)):
                        initInsnSet.append(i.ssa)

                        if dataflow_log_enabled:
                            print("trace from: ", curSsa.format())
                            print("in block: ", curSsa.getInst().basic_block.function_name)
                            print("to: ", i.ssa.format())
                            print("in block: ", i.basic_block.function_name)
                            print("\n\n")

                        if curSsa not in partialFlowGraph:
                            flow = list()
                            flow.append(i.ssa)
                            partialFlowGraph[curSsa] = flow
                        elif i.ssa not in partialFlowGraph[curSsa]:
                            partialFlowGraph[curSsa].append(i.ssa)
                        
                        # give every variable an entry to the flowgraph, even if it has no edge out
                        if i.ssa not in partialFlowGraph:
                            partialFlowGraph[i.ssa] = list()

            if curSsa.getImplicitUsages() != None:
                for usage in curSsa.getImplicitUsages():
                    if ((usage not in initInsnSet)
                    and (usage not in visitedInsnSet)):
                        initInsnSet.append(usage)

                        if dataflow_log_enabled:
                            print("trace from: ", curSsa.format())
                            print("in block: ", curSsa.getInst().basic_block.function_name)
                            print("\nto: ", usage.format())
                            print("\nin block: ", usage.getInst().basic_block.function_name)
                            print("\n\n")

                        if curSsa not in partialFlowGraph:
                            flow = list()
                            flow.append(usage)
                            partialFlowGraph[curSsa] = flow
                        elif usage not in partialFlowGraph[curSsa]:
                            partialFlowGraph[curSsa].append(usage)
                        
                        # give every variable an entry to the flowgraph, even if it has no edge out
                        if usage not in partialFlowGraph:
                            partialFlowGraph[usage] = list()
        
        return visitedInsnSet, partialFlowGraph


    
    # Yue: perform data flow analysis on a given variable or variable name or an instruction
    # 'idx' is the index of use var in the instruction for DFA
    # 'idx' is only useful when we track instruction
    # -1 means all useVars, 0 means the first, 1 means the second

    def doBackwardDFAForVarOrInsn(self, varOrInsn, idx=-1):
        # check if the given parameter is a variable or an instruction
        # if is an instruction, we put all its useVars for tracking
        varObjs = []
        partialFlowGraph = {}
        visitedInsnSet = list()
        initInsnSet = list()
        if isinstance(varOrInsn, SSA):
            if idx == -1:
                varObjs = varOrInsn.getUseVars()
            else:
                varObjs.append(varOrInsn.getUseVars()[idx])
            
            visitedInsnSet.append(varOrInsn)
            # Yue :add edges in the graph about the insturction itself to compare, we disable this for now
            # partialFlowGraph[varOrInsn] = list()

            for varObj in varObjs:
                varssa = varObj.getDefInsn().ssa
                if varssa not in partialFlowGraph:
                    partialFlowGraph[varssa] = list()
                # if varOrInsn not in partialFlowGraph[varssa]:
                #     partialFlowGraph[varssa].append(varOrInsn)

        elif not isinstance(varOrInsn, Variable):
            varObjs.append(next((x for x in self.variables if x.name == varOrInsn), None))
        else:
            varObjs.append(varOrInsn)

        if dataflow_log_enabled:
            print("Found for backward dataflow analysis:", str(varOrInsn))

        # add starting instruction in the graph
        for varObj in varObjs:
            varssa = varObj.getDefInsn().ssa
            visitedInsnSet.append(varssa)
            if varssa not in partialFlowGraph:
                partialFlowGraph[varssa] = list()
        
            
            # start from the def insns, see variables used in them
            for use_var in varssa.useVars: 
                use_var_insn = use_var.getDefInsn().ssa
                if use_var_insn not in initInsnSet:
                    initInsnSet.append(use_var_insn)
                    if use_var_insn not in partialFlowGraph:
                        partialFlowGraph[use_var_insn] = list()
                    if varssa not in partialFlowGraph[use_var_insn]:
                        partialFlowGraph[use_var_insn].append(varssa)
        

        while len(initInsnSet) != 0:
            curSsa = initInsnSet.pop()

            if curSsa not in visitedInsnSet:
                visitedInsnSet.append(curSsa)
            
            if dataflow_log_enabled:
                print("trace up to ssa\n", str(curSsa.format()))

            for useVar in curSsa.useVars:
                def_insn = useVar.getDefInsn().ssa
                if ((def_insn not in initInsnSet) 
                and (def_insn not in visitedInsnSet)):
                    initInsnSet.append(def_insn)

                if def_insn not in partialFlowGraph:
                    partialFlowGraph[def_insn] = list()
                if curSsa not in partialFlowGraph[def_insn]:
                    partialFlowGraph[def_insn].append(curSsa)
                # give every variable an entry to the flowgraph, even if it has no edge out
                if curSsa not in partialFlowGraph:
                    partialFlowGraph[curSsa] = list()

            
            if curSsa.getImplicitDefs() != None:
                for deff in curSsa.getImplicitDefs():
                    if ((deff not in initInsnSet)
                    and (deff not in visitedInsnSet)):
                        initInsnSet.append(deff)

                        if dataflow_log_enabled:
                            print("trace from: ", curSsa.format())
                            print("in block: ", curSsa.getInst().basic_block.function_name)
                            print("\nto: ", deff.format())
                            print("\nin block: ", deff.getInst().basic_block.function_name)
                            print("\n\n")

                        if curSsa not in partialFlowGraph:
                            flow = list()
                            flow.append(deff)
                            partialFlowGraph[curSsa] = flow
                        elif deff not in partialFlowGraph[curSsa]:
                            partialFlowGraph[curSsa].append(deff)
                        
                        # give every variable an entry to the flowgraph, even if it has no edge out
                        if deff not in partialFlowGraph:
                            partialFlowGraph[deff] = list()

        return visitedInsnSet, partialFlowGraph