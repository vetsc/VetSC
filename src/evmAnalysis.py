# The conversion to SSA is already done by the SSAEmulator
# when the CFG is reconstruct
# by default you have just to visualize it
import os
import networkx as nx

from octopus.arch.evm.model import Model
from octopus.arch.evm.model import SPECIAL_VARIABLES

from octopus.platforms.ETH.cfg import EthereumCFG
from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_MAINNET

import modelGeneration
import myUtility

from octopus.core.ssa import SSA


# currently, we do not include "ISZERO" because octopus seems to overuse it
CONDITIONAL_CHECK = ["LT", "GT", "EQ"]

# tp is transaction property
# entity means global variables in storage
# const is self-explanatory


class EvmAnalysis:

    def __init__(self, model):
        self.model = model

        # these data structures store the offsets of the storage where the transaction property is stored
        self.transaction_property_mstore = {}

        # this stores entities (variable in storage) that have direct data dependency with transaction properties
        self.transaction_property_sstore = {}


        # these dictionaries are to store the backward DFA on the offsets of all storage/memory operations
        self.sstore_idxgraph = {}
        self.sload_idxgraph = {}
        self.mstore_idxgraph = {}
        self.mload_idxgraph = {}


        # tpToConstOrCall[tpssa] = const.ssa/call.ssa
        # from tpssa -> tpInstruction -> block -> function
        # tpToCall[tp_ssa] = callInsn.ssa
        self.tpToConsts = {}

        # stores the second and third arguments from tp or entity for a call
        # second arg: address
        # third arg: value
        # sendToArgs[ssa] = (addr_ssa, value_ssa)
        self.sendToArgs = {}
        # sendToCondition[ssa] = (funcName, condition)
        self.sendToCondition = {}

        # entity is a index to storage
        #######################################################
        # entityToFunction[ssa] = func_hashes, list of functions that entity appears
        self.entityToFuncHashes = {}


        # entityToCOndandValue[ssa] = cond_value_list
        # cond_value_list.append((func_hash, (first_op, second_op, operator_ssa, has_two_iszero), value))
        # three items: function, condition, value
        self.entityToCondandValueList = {}

        # entityToIdx[ssa] = idx
        self.entityToIdx = {}

        # contain all the entities that have const value
        self.const_entity_list = list()
        #######################################################

        # store the function and its revert conditions
        # op can be tp/entity/const ssa
        # funcToRevertCond[funcName] = (first_op, second_op, operator_ssa, has_two_iszero)
        self.funcToRevertCond = {}





    # this helper function returns a list, which contains all the const-valued entities
    def getConstEntities(self):
        for entity in self.entityToCondandValueList:
            cond_value_list = self.entityToCondandValueList[entity]
            hasVar = False
            for (_func, _cond, value_ssa) in cond_value_list:
                if not value_ssa.is_constant:
                    hasVar = True
                    break
            if not hasVar:
                self.const_entity_list.append(entity)



    # we perform dataflow on mem and storage operations
    def trackMemStorageOps(self):
        funcName = "*"
        # for memory and storage operations, we keep track of the offsets
        insnName = "SSTORE"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns:
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.sstore_idxgraph:
                    self.sstore_idxgraph[insn.ssa] = bwfg
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/sstore/" + "sstore_" + insn.name + str(insn.offset) + ".dot")

                # for sstore, we also store the value
                

        insnName = "MSTORE"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns:
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.mstore_idxgraph:
                    self.mstore_idxgraph[insn.ssa] = bwfg
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/mstore/" + "mstore_" + insn.name + str(insn.offset) + ".dot")


        insnName = "MSTORE8"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns:
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.mstore_idxgraph:
                    self.mstore_idxgraph[insn.ssa] = bwfg
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/mstore/" + "mstore8_" + insn.name + str(insn.offset) + ".dot")


        insnName = "SLOAD"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns: 
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.sload_idxgraph:
                    self.sload_idxgraph[insn.ssa] = bwfg
                    # print("adding", insn.ssa.format(), " in sload_idxgraph", insn.offset)
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/sload/" + "ssload_" + insn.name + str(insn.offset) + ".dot")


        insnName = "SHA3"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns:
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.mload_idxgraph:
                    self.mload_idxgraph[insn.ssa] = bwfg
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/sha3/" + "sha3_" + insn.name + str(insn.offset) + ".dot")

        insnName = "KECCAK256"
        insns = self.model.getInsnsFromFuncs(insnName, funcName)
        if insns:
            for insn in insns:
                _, bwfg = self.model.doBackwardDFAForVarOrInsn(insn.ssa, 0)
                if insn.ssa not in self.mload_idxgraph:
                    self.mload_idxgraph[insn.ssa] = bwfg
                # myUtility.flowGraph_to_dot_file(bwfg, os.getcwd() + "/mem_storage_ops/sha3/" + "keccak256_" + insn.name + str(insn.offset) + ".dot")


    def linkDataFlow(self):
        smatched = myUtility.doMatching(self.sstore_idxgraph, self.sload_idxgraph)
        mmatched = myUtility.doMatching(self.mstore_idxgraph, self.mload_idxgraph)

        for pair in smatched:
            storeInsnssa = pair[0]
            loadInsnssa = pair[1]

            if storeInsnssa.getInst().basic_block.function_name != loadInsnssa.getInst().basic_block.function_name:
                # print("linking sload to sstore: ", loadInsnssa.format(), storeInsnssa.format())
                # once we find a match, we add the implicit dataflow into def-use chain
                storeInsnssa.addImplicitUsages(loadInsnssa)
                loadInsnssa.addImplicitDefs(storeInsnssa)
        
        for pair in mmatched:
            storeInsnssa = pair[0]
            loadInsnssa = pair[1]

            # only perform linking, if store is before load.
            # that means, 
            # 1. if the load and store are in the same block, we compare instr offset
            # 2. the offset_store is precedessor of block_load
            # 
            block_store = storeInsnssa.instr.basic_block
            block_load = loadInsnssa.instr.basic_block

            if (block_load == block_load and storeInsnssa.instr.offset < loadInsnssa.instr.offset) or (myUtility.isPred(block_store, block_load)):
                # print("linking mload to mstore: ", loadInsnssa.format(), storeInsnssa.format())

                # once we find a match, we add the implicit dataflow into def-use chain
                storeInsnssa.addImplicitUsages(loadInsnssa)
                loadInsnssa.addImplicitDefs(storeInsnssa)



    def specialVarTracking(self, tp, funcHash):
        fw_insnSet = {}
        fw_graph = {}

        tpVars = self.model.retrieveSepcialVar(tp, funcHash)
        if not tpVars:
            return

        # for every transaction property, we find the instructions associated with the call, do forward dataflow analysis on its defined var. 
        for tpVar in tpVars:
            print("Keeping track of variable: ", tpVar)
            insnSet, fwfg = self.model.doForwardDFAForVar(tpVar)
            tp_ssa = tpVar.getDefInsn().ssa
            fw_insnSet[tp_ssa] = insnSet
            fw_graph[tp_ssa] = fwfg

            # for every var in the forward analysis, we extract all instructions that use the special var
            # Specifically, we deal with 3 cases
            # 1). special var is stored in memory or storage
            # 2). special var is compared with some variable
            # 3). special var is used by a CALL()

            # condVars and callArgs are the getUseVars() of the conparison or call ssa
            conditions, callArgs, _storeVars = myUtility.getConditionalCheckOrCallOrStoreVars(insnSet)

            # handleStorageVars(model, tp, storeVars, insnSet, fwfg)
            if len(conditions) != 0:
                self.handleConditionCheck(tp_ssa, tp, conditions, insnSet, fwfg, funcHash)
            
            if len(callArgs) != 0:
                self.handleCallArgs(tp_ssa, tp, callArgs, insnSet, fwfg, funcHash)
            
            self.checkDepBBsForSstore(conditions, insnSet, fwfg, funcHash)

            # for function, we check its revert conditions
            # and record them if the condition is related to tp or entity
            # funcToRevertCond[funcName] = {list(conditions)}
            self.extractFuncToRevertCond(funcHash, tp_ssa, conditions, insnSet)
            

            myUtility.flowGraph_to_dot_file(fwfg, os.getcwd() + "/" + tpVar.name + ".dot")




    # check if the given defssa is from tp, entity or const
    # if so, return the list of values of the definition 
    def getValue(self, defssa):
        
        values = list()

        if defssa.is_constant:
            values.append(defssa.args)
        else:
            ssaSet, _bwfg = self.model.doBackwardDFAForVarOrInsn(defssa)
            sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
            if sload_ssa != None:
                values.append(sload_ssa)
            for bwssa in ssaSet:
                if bwssa.method_name in SPECIAL_VARIABLES:
                    values.append(bwssa)
        
        return values


    def retrieveValueFromStore(self, store_ssa):
        return self.getValue(store_ssa.getUseVars()[1].getDefInsn().ssa)






    def startAnalysis(self):
        # 1. we perform backward dataflow analysis on memory and storage operations
        self.trackMemStorageOps()
        # 2. then we try to match them to link up the missing dataflow
        self.linkDataFlow()

        # 3. find entities 
        print("Analysing all tps in the whole smart contract")
        self.specialVarTracking("*", "*")

        # # 4. identify entities' value, condition
        # self.getConstEntities()

        # for entity_ssa in self.entityToFuncHashes:
        #     # care store only. three possible sources: const, tp, and other entity
        #     if entity_ssa in self.sstore_idxgraph:
        #         value = self.retrieveValueFromStore(entity_ssa)

        #         # then try to find precedessor basic block and find condition
        #         # we only care if the condition involves tp, entity and const
        #         # tp has been taken care by checkDepBBsForSstore








            
            


    # we first identify the control-dependent blocks, and then see if any sstore exists
    def checkDepBBsForSstore(self, conditions, insnSet, fwfg, funcHash):
        
        depBBs = list()
        depBBToConditionVar = {}

        varToCondMapping = {}
        realCondVars = list()
        for cond in conditions:
            newCond = list()
            newCond.append(self.getValue(cond[0].getDefInsn().ssa))
            newCond.append(self.getValue(cond[1].getDefInsn().ssa))
            newCond.append(cond[2])
            # check the operator_ssa 's has_two_iszero
            instr = cond[2].instr
            
            if not instr.next_instr or not instr.next_instr.next_instr:
                continue
            has_two_iszero = False

            if instr.next_instr.name == "ISZERO" and instr.next_instr.next_instr.name == "ISZERO":
                nextIn = instr.next_instr.next_instr
                if nextIn.next_instr and nextIn.next_instr.name != "ISZERO":
                    has_two_iszero = True
            
            print("has_two: ", cond[0].getDefInsn().ssa.format(), cond[1].getDefInsn().ssa.format(), instr.ssa.format(), has_two_iszero)
            newCond.append(has_two_iszero)

            varToCondMapping[cond[0]] = newCond
            varToCondMapping[cond[1]] = newCond
            realCondVars.append(cond[0])
            realCondVars.append(cond[1])

        
        # realCondVars.extend([cond[0] for cond in conditions])
        # realCondVars.extend([cond[1] for cond in conditions])
        if len(realCondVars) == 0:
            return


        # we try to find control dependent blocks to the conditional statements
        for ccVar in realCondVars:
            sv_bb = ccVar.getDefInsn().basic_block
            currBBs = list()
            currBBs.extend(sv_bb.next_bbs)

            # we find all the dependent basic blocks
            while len(currBBs) != 0:
                cur_bb = currBBs.pop()

                # check if cur_bb's prev_bb is its immediate dominator
                # TODO: should check if sv_bb is cur_bb's dominator, but let's just do this for now
                if len(cur_bb.prev_bbs) != 1:
                    continue
                
                depBBs.append(cur_bb)

                if cur_bb not in depBBToConditionVar:
                    depBBToConditionVar[cur_bb] = list()
                if ccVar not in depBBToConditionVar[cur_bb]:
                    depBBToConditionVar[cur_bb].append(ccVar)

                # only add if jumpi is the last instruction
                if cur_bb.end_instr.name != "JUMPI":
                    continue

                for next_bb in cur_bb.next_bbs:
                    if (next_bb not in currBBs 
                    and next_bb not in depBBs):
                        currBBs.append(next_bb)

        # we then try to find the sstore ops in the dependent blocks
        for dep_bb in depBBs:

            bbssas = list()
            for insn in dep_bb.instructions:
                if insn.ssa != None:
                    bbssas.append(insn.ssa)

            _, _, storeVars = myUtility.getConditionalCheckOrCallOrStoreVars(bbssas) 

            for storeSsa, svar in storeVars.items():
                if storeSsa.method_name == 'SSTORE':
                    # fwfg add the ssa in
                    ccVars = depBBToConditionVar[dep_bb]
                    sVarDefssa = svar.getDefInsn().ssa

                    # link storeSsa to the JUMPI of conditional var block
                    for ccVar in ccVars:
                        jumpissa = ccVar.getDefInsn().basic_block.end_instr.ssa
                        if storeSsa not in fwfg[jumpissa]:
                            fwfg[jumpissa].append(storeSsa)
                        if storeSsa not in fwfg:
                            fwfg[storeSsa] = list()
                    
                    # add this sstore into our graph
                    if sVarDefssa not in insnSet:
                        _ssaSet,bwfg = self.model.doBackwardDFAForVarOrInsn(svar)
                        myUtility.graphMerge(fwfg, bwfg)

                    # storeSsa can become a new entity
                    self.addEntity(storeSsa, funcHash)

                    # add condition to this sstore
                    # one sstore can have multiple conditions
                    for ccVar in ccVars:
                        print(storeSsa.format())
                        values = self.retrieveValueFromStore(storeSsa)
                        value = values[0]
                        for v in values:
                            if myUtility.isTP(v):
                                value = v

                        v1 = varToCondMapping[ccVar][0]
                        v1Value = v1
                        if not isinstance(v1, int):
                            v1Value = v1[0]
                            for v in v1:
                                if myUtility.isTP(v):
                                    v1Value = v
                        v2 = varToCondMapping[ccVar][1]
                        v2Value = v2
                        if not isinstance(v2, int):
                            v2Value = v2[0]
                            for v in v2:
                                if myUtility.isTP(v):
                                    v2Value = v

                        cond_value_list = (funcHash, (v1Value,v2Value,varToCondMapping[ccVar][2], varToCondMapping[ccVar][3]), value)
                        operator_ssa = varToCondMapping[ccVar][2]

                        sv_bb = operator_ssa.instr.basic_block
                        next_bbs = list()
                        next_bbs.extend(sv_bb.next_bbs)
                        hasRevert = False
                        for next_bb in next_bbs:
                            if len(next_bb.next_bbs) == 0:
                                hasRevert = True
                                break
                        if hasRevert == True:
                            continue

                        
                        print("\n\nvar1: ", v1Value.format())
                        if isinstance(v2Value, SSA):
                            print("var2: ", v2Value.format())
                        else:
                            print("var2: ", v2Value)
                        print("op: ", operator_ssa.format())
                        print("value: ", value.format(), "\n\n")
                        instr = operator_ssa.instr

                        # value cannot be from itself
                        idxValue = self.checkIdxForStorage(value)
                        idxStore = self.checkIdxForStorage(storeSsa)
                        if idxValue > -1 and idxStore > -1 and idxValue == idxStore:
                            continue 

                        
                        

                        if storeSsa not in self.entityToCondandValueList:
                            self.entityToCondandValueList[storeSsa] = list()
                        if cond_value_list not in self.entityToCondandValueList[storeSsa]:
                            self.entityToCondandValueList[storeSsa].append(cond_value_list)




    def saveToFuncToRevertCond(self, insnSet, funcHash, tp_ssa, operator_ssa, var1_defssa, var2_defssa):
        instr = operator_ssa.instr

        has_two_iszero = False
        if instr.next_instr.name == "ISZERO" and instr.next_instr.next_instr.name == "ISZERO":
                nextIn = instr.next_instr.next_instr
                if nextIn.next_instr and nextIn.next_instr.name != "ISZERO":
                    has_two_iszero = True


        # one of the var1 and var2 must be a tp since the condition is from a tp dataflow analysis
        # therefore, if var1 not in insnset, that means var2 is tp
        if var1_defssa not in insnSet:
            # a tp is compared directly with a constant
            if var1_defssa.is_constant:
                if funcHash not in self.funcToRevertCond:
                    self.funcToRevertCond[funcHash] = list()
                # print("\n1for func: ", funcHash)
                # print("\trevert cond const: ", tp_ssa.format(), var1_defssa.args, operator_ssa.format(), "\n")
                if (var1_defssa.args, tp_ssa, operator_ssa, has_two_iszero) not in self.funcToRevertCond[funcHash]:
                    self.funcToRevertCond[funcHash].append((var1_defssa.args, tp_ssa, operator_ssa, has_two_iszero))
            else:
                # if not a constant, we do backward dataflow
                ssaSet, _bwfg = self.model.doBackwardDFAForVarOrInsn(var1_defssa)

                # now we check if a tp is compared with a sload
                sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
                if sload_ssa != None:
                    if funcHash not in self.funcToRevertCond:
                        self.funcToRevertCond[funcHash] = list()
                    # print("\n1for func: ", funcHash)
                    # print("\trevert cond: ", tp_ssa.format(), sload_ssa.format(), operator_ssa.format(), "\n")
                    if (sload_ssa, tp_ssa, operator_ssa, has_two_iszero) not in self.funcToRevertCond[funcHash]:
                        self.funcToRevertCond[funcHash].append((sload_ssa, tp_ssa, operator_ssa, has_two_iszero))
        else:
            # var1 is tp
            if var2_defssa.is_constant:
                if funcHash not in self.funcToRevertCond:
                    self.funcToRevertCond[funcHash] = list()
                # print("\n2for func: ", funcHash)
                # print("\trevert cond const: ", tp_ssa.format(), var2_defssa.args, operator_ssa.format(), "\n")
                if (tp_ssa, var2_defssa.args, operator_ssa, has_two_iszero) not in self.funcToRevertCond[funcHash]:
                    self.funcToRevertCond[funcHash].append((tp_ssa, var2_defssa.args, operator_ssa, has_two_iszero))
            else:
                # if not a constant, we do backward dataflow
                ssaSet, _bwfg = self.model.doBackwardDFAForVarOrInsn(var2_defssa)

                # now we check if a tp is compared with a sload
                sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
                if sload_ssa != None:
                    if funcHash not in self.funcToRevertCond:
                        self.funcToRevertCond[funcHash] = list()
                    # print("\n2for func: ", funcHash)
                    # print("\trevert cond: ", tp_ssa.format(), sload_ssa.format(), operator_ssa.format(), "\n")
                    if (tp_ssa, sload_ssa, operator_ssa, has_two_iszero) not in self.funcToRevertCond[funcHash]:
                        self.funcToRevertCond[funcHash].append((tp_ssa, sload_ssa, operator_ssa, has_two_iszero))



    # TODO: do the same for entity
    def extractFuncToRevertCond(self, funcHash, tp_ssa, conditions, insnSet):

        for condition in conditions:
            opVar1 = condition[0]
            opVar2 = condition[1]
            operator_ssa = condition[2]

            sv_bb = operator_ssa.instr.basic_block
            next_bbs = list()
            next_bbs.extend(sv_bb.next_bbs)
            hasRevert = False
            for next_bb in next_bbs:
                if len(next_bb.next_bbs) == 0:
                    hasRevert = True
                    break
            if hasRevert == False:
                continue

            var1_defssa = opVar1.getDefInsn().ssa
            var2_defssa = opVar2.getDefInsn().ssa

            self.saveToFuncToRevertCond(insnSet, funcHash, tp_ssa, operator_ssa, var1_defssa, var2_defssa)











    # storeVars stores all the offsets of the MSTORE or SSTORE.
    # we do backward DFA on them
    def handleStorageVars(self, specialVar, storeVars, insnSet, fwfg):
        for key, svar in storeVars.items():
            # As long as the var is not in insnSet, that means we find the var that is not the transaction property value.
            sVarDefssa = svar.getDefInsn().ssa
            if sVarDefssa not in insnSet:
                _ssaSet,bwfg = self.model.doBackwardDFAForVarOrInsn(svar)
                myUtility.graphMerge(fwfg, bwfg)
                if 'MSTORE' in key.method_name:
                    if specialVar not in self.transaction_property_mstore:
                        self.transaction_property_mstore[specialVar] = list()
                    self.transaction_property_mstore[specialVar].append(bwfg)
                else:
                    if specialVar not in self.transaction_property_sstore:
                        self.transaction_property_sstore[specialVar] = list()
                    self.transaction_property_sstore[specialVar].append(bwfg)



    # 1. record the comparison activity.
    # 2. keep track of the compared value (const or variable)
    # 3. do backward DFA on the variable
    def handleConditionCheck(self, tp_ssa, specialVar, condVars, insnSet, fwfg, funcHash):
        realCondVars = list()
        realCondVars.extend([item[0] for item in condVars])
        realCondVars.extend([item[1] for item in condVars])

        for ccVar in realCondVars:
            # As long as the var is not in insnSet, that means we find the value that is compared with some non-tp value.
            ccVarDefssa = ccVar.getDefInsn().ssa
            if ccVarDefssa not in insnSet:
                
                # a tp is compared directly with a constant
                if ccVarDefssa.is_constant:
                    self.tpToConsts[tp_ssa] = ccVarDefssa

                    if ccVarDefssa not in fwfg:
                        fwfg[ccVarDefssa] = list()
                    for varssa in insnSet:
                        if ccVar in varssa.getUseVars():
                            fwfg[ccVar.getDefInsn().ssa].append(varssa)
                    continue

                # if not a constant, we do backward dataflow
                ssaSet,bwfg = self.model.doBackwardDFAForVarOrInsn(ccVar)
                myUtility.graphMerge(fwfg, bwfg)

                # now we check if a tp is compared with a sload
                sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
                if sload_ssa != None:
                    self.addEntity(sload_ssa, funcHash)


                # now that we have the backward graph for each value that is compared with the global var, we check if the value is from SLOAD() and keep a record of the offset
                # if specialVar not in gv_comp_sload:
                #     gv_comp_sload[specialVar] = list()
                # gv_comp_sload[specialVar].append(checkFuncs(ssaSet, bwfg, "SLOAD"))

                # if specialVar not in gv_comp_sha3:
                #     gv_comp_sha3[specialVar] = list()
                # gv_comp_sha3[specialVar].append(checkFuncs(ssaSet, bwfg, "SHA3"))


                


    # we handle the call arguments by perform backward DFA on them
    def handleCallArgs(self, tp_ssa, specialVar, callArgs, insnSet, fwfg, funcHash):
        # for the second and third arguments, we check if it is from tp or storage or const, and record accordingly
        addrVar = callArgs[1]
        valueVar = callArgs[2]

        addrFrom = None
        valueFrom = None
        callInsn = None

        for insn in addrVar.getUseInsns():
            if insn.is_call and funcHash in insn.basic_block.function_name:
                callInsn = insn
                break
        if not callInsn:
            return

        print("1", addrFrom, tp_ssa.format())
        # As long as the var is not in insnSet, that means we find the var that is not the tp
        cVarDefssa = addrVar.getDefInsn().ssa
        if cVarDefssa not in insnSet:
            ssaSet,bwfg = self.model.doBackwardDFAForVarOrInsn(addrVar)
            myUtility.graphMerge(fwfg, bwfg)
            sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
            if sload_ssa != None:
                self.addEntity(sload_ssa, funcHash)
                addrFrom = sload_ssa
            else:
                another_tp_ssa = myUtility.findMethodInSet(ssaSet, SPECIAL_VARIABLES)
                # addr directly from a constant
                if another_tp_ssa != None:
                    addrFrom = another_tp_ssa
                elif cVarDefssa.is_constant:
                    addrFrom = cVarDefssa
        else: #cvar is from tp
            addrFrom = tp_ssa

        # do it again for the third argument
        valueVarDefssa = valueVar.getDefInsn().ssa
        if valueVarDefssa not in insnSet:
            ssaSet,bwfg = self.model.doBackwardDFAForVarOrInsn(valueVar)
            myUtility.graphMerge(fwfg, bwfg)

            sload_ssa = myUtility.findMethodInSet(ssaSet, "SLOAD")
            if sload_ssa != None:
                self.addEntity(sload_ssa, funcHash)
                valueFrom = sload_ssa
            else:
                another_tp_ssa = myUtility.findMethodInSet(ssaSet, SPECIAL_VARIABLES)
                print("4", cVarDefssa.format())
                # addr directly from a constant
                if another_tp_ssa != None:
                    valueFrom = another_tp_ssa
                 # value directly from a constant
                elif valueVarDefssa.is_constant:
                    valueFrom = valueVarDefssa
        else: #cvar is from tp
            valueFrom = tp_ssa

        self.sendToArgs[callInsn.ssa] = (funcHash, addrFrom, valueFrom)













    # this function finds all the variables that are dependent on the given var in the flow graph
    # DEPRECATED: should use model.doBackwardDFAForVarOrInsn()
    # def findAllDependentSSAs(ssa, flowgraph):
    #     dependents = {}
        
    #     ssaSet = list()
    #     ssaSet.append(ssa)
    #     # TODO: I eliminated the loop in flow analysis?
    #     while len(ssaSet) != 0:
    #         curSsa = ssaSet.pop()
    #         if curSsa not in dependents:
    #             dependents[curSsa] = list()

    #         for def_ssa, use_ssas in flowgraph.items():
    #             if curSsa in use_ssas:
    #                 if def_ssa not in dependents:
    #                     dependents[def_ssa] = list()
    #                 if curSsa not in dependents[def_ssa]:
    #                     dependents[def_ssa].append(curSsa)
    #                 ssaSet.append(def_ssa)
    #     return dependents





    # check if the given ssa is in our entity list, if also, return the index of it
    def checkIdxForStorage(self, s_ssa):
        if s_ssa.method_name == "SSTORE":
            newIdx = self.sstore_idxgraph[s_ssa]
        elif s_ssa.method_name == "SLOAD":
            newIdx = self.sload_idxgraph[s_ssa]
        else:
            return -2

        matched_ssa = None
        for oldssa in self.entityToFuncHashes:
            if oldssa.method_name == "SSTORE":
                oldidx = self.sstore_idxgraph[oldssa]
            else:
                oldidx = self.sload_idxgraph[oldssa]
            dis = myUtility.distanceFromIdx(newIdx, oldidx)
            if dis == 0:
                matched_ssa = oldssa
                break
            
        if not matched_ssa:
            return -1
        else:
            idx = self.entityToIdx[matched_ssa]
            return idx


    # once we find an entity (index to storage), we store it here
    def addEntity(self, ssa, funcHash):
        idx = self.checkIdxForStorage(ssa)
        if idx == -1:
            if ssa not in self.entityToFuncHashes:
                self.entityToFuncHashes[ssa] = list()
            self.entityToFuncHashes[ssa].append(funcHash)
            self.entityToIdx[ssa] = len(self.entityToIdx) + 1
            print("adding entity: ", ssa.format(), " with func: ", funcHash, " instr offset: ", ssa.instr.offset ," and idx: ", self.entityToIdx[ssa])