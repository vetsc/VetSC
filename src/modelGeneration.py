import os
import evmAnalysis
from octopus.core.ssa import SSA


def generateVAR(evmAnalysis):
    var_string = ""
    var_string += "\tVAR\n"
    
    # write function names
    funcNames = list()
    for (_tp_sem, func_sem) in evmAnalysis.tp_func_sem_info.values():
        if func_sem not in funcNames:
            funcNames.append(func_sem)
    funcNames.append("main")
    var_string += "\t\tfunc: {" + ", ".join(funcNames) + "};\n"
    

    # write execution state variable
    var_string += "\t\texecutionState: {normal, revert};\n"
    

    # write transaction properties
    for tp_sem in evmAnalysis.sem_tpFunc_mapping:
        var_string += "\t\t" + tp_sem + ": 0..100;\n"
    

    # write all entities in functions
    for ssa in evmAnalysis.entityToFuncHashes:
        if ssa not in evmAnalysis.const_entity_list:
            var_string += "\t\ts" + str(evmAnalysis.entityToIdx[ssa]) + ": 0..100;\n"
        else:
            consts = evmAnalysis.entityToCondandValueList[ssa]
            var_string += "\t\ts" + str(evmAnalysis.entityToIdx[ssa]) + ":{" + ", ".join(consts) + "}:\n"
    
    # write call in
    # each send will create three variables in smv: 
    # sendState, receiver and sendValue
    # sendToArgs[ssa] = (addr_ssa, value_ssa)
    sendIdx_ssa_mapping = {}
    idx = 0
    for send_ssa in evmAnalysis.sendToArgs:
        idx = idx + 1
        sendIdx_ssa_mapping[send_ssa] = idx
        var_string += "\t\tsendState" + str(idx) + ": boolean;\n"
        var_string += "\t\treceiver" + str(idx) + ": 0..100;\n"
        var_string += "\t\tsendValue" + str(idx) + ": 0..100;\n"

    return var_string


def generateINIT(evmAnalysis):
    init_string = ""

    # init func
    init_string += "\t\tinit(func) := main;\n\n"

    # init execution state variable
    init_string += "\t\tinit(executionState) := normal;\n"

    # init transaction properties
    for tp_sem in evmAnalysis.sem_tpFunc_mapping:
        init_string += "\t\tinit(" + tp_sem + ") := 0;\n"
    
    # init entities in functions
    for ssa in evmAnalysis.entityToFuncHashes:
        if ssa not in evmAnalysis.const_entity_list:
            init_string += "\t\tinit(s" + str(evmAnalysis.entityToIdx[ssa]) + ") := 0..100;\n"
        else:
            consts = [x[1] for x in evmAnalysis.entityToCondandValueList.values()]
            init_string += "\t\ts" + str(evmAnalysis.entityToIdx[ssa]) + ":{" + ", ".join(consts) + "}:\n"
    
    # write call in
    # each send will create three variables in smv: 
    # sendState, receiver and sendValue
    # sendToArgs[ssa] = (addr_ssa, value_ssa)
    idx = 0
    for _send_ssa in evmAnalysis.sendToArgs:
        idx = idx + 1
        init_string += "\t\tinit(sendState" + str(idx) + ") := FALSE;\n"
        init_string += "\t\tinit(receiver" + str(idx) + ") := 0;\n"
        init_string += "\t\tinit(sendValue" + str(idx) + ") := 0;\n"

    return init_string


# find function semantic meaning with the given function hash
def findFuncSem(funcHash, evmAnalysis):
    for (_tp, f_hash) in evmAnalysis.tp_func_sem_info:
        (_tp_sem, func_sem) = evmAnalysis.tp_func_sem_info[(_tp, f_hash)]
        if f_hash == funcHash:
            return func_sem


def generateTrasition(evmAnalysis):
    trans_string = ""

    # write function transition
    funcNames = list()
    for (_tp_sem, func_sem) in evmAnalysis.tp_func_sem_info.values():
        if func_sem not in funcNames:
            funcNames.append(func_sem)
    trans_string += "\t\tnext(func) := {" + ", ".join(funcNames) + "};\n\n"
    

    # write execution state transition
    trans_string += "\t\tnext(executionState) :=\n\t\tcase\n"
    for func_hash in evmAnalysis.funcToRevertCond:
        # tuples : (operand1, operand2, operator, has_two_iszero)
        tuples = evmAnalysis.funcToRevertCond[func_hash]
        for (op1, op2, op, has_two_iszero) in tuples:
            op1Value = getValue(evmAnalysis, func_hash, op1)
            op2Value = getValue(evmAnalysis, func_hash, op2)
            func_sem = findFuncSem(func_hash, evmAnalysis)
            trans_string += "\t\t\tfunc = " + func_sem + " & " + op1Value + evmAnalysis.condOp_to_sign(op.method_name, has_two_iszero) + op2Value + " : revert;\n"
    trans_string += "\t\t\tTRUE : normal;\n"
    trans_string += "\t\tesac;\n\n"
    

    # write transaction properties transitions
    for tp_sem in evmAnalysis.sem_tpFunc_mapping:
        trans_string += "\t\tnext(" + tp_sem + ") :=\n\t\tcase\n"

        tp_func_list = evmAnalysis.sem_tpFunc_mapping[tp_sem]
        for (_tp, func) in tp_func_list:
            func_sem = findFuncSem(func, evmAnalysis)
            trans_string += "\t\t\tfunc = " + func_sem + " & " + tp_sem + " != 100 : 1..100;\n"
        trans_string += "\t\t\tTRUE : 0;\n"
        trans_string += "\t\tesac;\n\n"
    

    # write entity transitions
    for ssa in evmAnalysis.entityToIdx:
        idx = evmAnalysis.entityToIdx[ssa]
        if ssa in evmAnalysis.entityToCondandValueList:
            func_cond_value_list = evmAnalysis.entityToCondandValueList[ssa]

            trans_string += "\t\tnext(s" + str(evmAnalysis.entityToIdx[ssa]) + ") :=\n\t\tcase\n"

            for func_cond_value in func_cond_value_list:
                func_hash = func_cond_value[0]
                cond = func_cond_value[1]
                value = func_cond_value[2]
                op1 = cond[0]
                op2 = cond[1]
                op = cond[2]
                has_two_iszero = cond[3]
                
                op1Value = getValue(evmAnalysis, func_hash, op1)
                op2Value = getValue(evmAnalysis, func_hash, op2)
                print("value: ", value.format())
                value = getValue(evmAnalysis, func_hash, value)

                func_sem = findFuncSem(func_hash, evmAnalysis)

                trans_string += "\t\t\tfunc = " + func_sem + " & " + op1Value + evmAnalysis.condOp_to_sign(op.method_name, has_two_iszero) + op2Value + " : " + value + ";\n"

            trans_string += "\t\t\tTRUE : s" + str(evmAnalysis.entityToIdx[ssa]) + ";\n"
            trans_string += "\t\tesac;\n\n"
        else:
            trans_string += "\t\tnext(s" + str(idx) + ") := s" + str(idx) + ";\n\n"

    # write call in
    # each send will create three variables in smv: 
    # sendState, receiver and sendValue
    # sendToArgs[ssa] = (addr_ssa, value_ssa)
    sendIdx_ssa_mapping = {}
    idx = 0
    for send_ssa in evmAnalysis.sendToArgs:
        idx = idx + 1
        sendIdx_ssa_mapping[send_ssa] = idx

        (funcHash, addrFrom, valueFrom) = evmAnalysis.sendToArgs[send_ssa]
        func_sem = findFuncSem(funcHash, evmAnalysis)

        addrFrom = getValue(evmAnalysis, funcHash, addrFrom)
        valueFrom = getValue(evmAnalysis, funcHash, valueFrom)

        # sendState
        trans_string += "\t\tnext(sendState" + str(idx) + ") :=\n\t\tcase\n"
        trans_string += "\t\t\tfunc = " + func_sem + " & executionState != revert : TRUE;\n"
        trans_string += "\t\t\tTRUE : sendState;\n"
        trans_string += "\t\tesac;\n\n"

        # receiver
        trans_string += "\t\tnext(receiver" + str(idx) + ") :=\n\t\tcase\n"
        trans_string += "\t\t\tsendState" + str(idx) + " = FALSE : 0;\n"
        trans_string += "\t\t\tTRUE : " + addrFrom + ";\n"
        trans_string += "\t\tesac;\n\n"

        # sendValue
        trans_string += "\t\tnext(sendValue" + str(idx) + ") :=\n\t\tcase\n"
        trans_string += "\t\t\tsendState" + str(idx) + " = FALSE : 0;\n"
        trans_string += "\t\t\tTRUE : " + valueFrom + ";\n"
        trans_string += "\t\tesac;\n\n"


    return trans_string



def getValue(evmAnalysis, func_hash, givenInput):
    value = None
    if isinstance(givenInput, SSA):
        idx = evmAnalysis.checkIdxForStorage(givenInput)
        if idx != -2 and idx != -1:
            value = 's' + str(idx)
        else:
            #print("input:", givenInput.format(), " func: ", func_hash)
            value = evmAnalysis.tp_func_sem_info[(givenInput.method_name, func_hash)][0]
            #print("value", value)
    if isinstance(givenInput, int):
        value = str(givenInput)
    return value




def generateModel(contractName, evmAnalysis):
    
    model_string = ""
    model_string += "MODULE " + contractName + "()\n"
    model_string += generateVAR(evmAnalysis)
    model_string += "\tASSIGN\n"
    model_string += generateINIT(evmAnalysis)
    model_string += generateTrasition(evmAnalysis)
        
        
        
    with open(os.getcwd() + "/" + contractName + ".smv", "w") as file:
        file.write(model_string)
        file.write("\t\t")
