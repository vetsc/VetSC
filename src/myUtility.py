import os
import networkx as nx
import editdistance

from octopus.core.ssa import SSA 
import evmAnalysis

def flowGraph_to_dot_file(flowgraph, filePath):
    ssaDic = {}
    i = 0

    with open(filePath, "w") as file:
        file.write("digraph G {\n")

        # write all the nodes first
        for ssa in flowgraph:
            if ssa not in ssaDic:
                ssa_sig = "\"" + ssa.format() + "\""
                ssaDic[ssa] = i
                file.write(str(i) + "[label=" + ssa_sig + "]\n")
                i = i + 1

            if len(flowgraph[ssa]) == 0:
                continue

            for target in flowgraph[ssa]:
                if target not in ssaDic:
                    target_sig = "\"" + target.format() + "\""
                    ssaDic[target] = i
                    file.write(str(i) + "[label=" + target_sig + "]\n")
                    i = i + 1

        # then write down all the edges
        for ssa in flowgraph: 
            tolist = flowgraph[ssa]
            for target in tolist:
                file.write(str(ssaDic[ssa]) + " -> " + str(ssaDic[target]) + "\n")
        file.write("}")
    return


# convert our flowgraph into a networkx DiGraph
def to_nx_graph(flowgraph):
    g = nx.DiGraph()
    nodeDic = {}
    i = 0

    # first index all the nodes into a dictionary
    for defssa in flowgraph:
        if defssa not in nodeDic:
            nodeDic[defssa] = i
            i = i + 1
        for usessa in flowgraph[defssa]:
            if usessa not in nodeDic:
                nodeDic[usessa] = i
                i = i + 1
    
    # then we add nodes and edges into a networkx DiGraph
    for ssa in nodeDic:
        g.add_node(nodeDic[ssa])
        g.nodes[nodeDic[ssa]]['label'] = ssa.normalized_format()
        
        if ssa in flowgraph:
            for usessa in flowgraph[ssa]:
                g.add_edge(nodeDic[ssa], nodeDic[usessa])
    return g



def node_sub_cost(node1, node2):
    return editdistance.eval(node1['label'], node2['label'])

def node_del_cost(node):
    return len(node['label'])

def node_ins_cost(node):
    return len(node['label'])


# merge the two graphs together
def graphMerge(flowgraph1, flowgraph2):
    for insn2 in flowgraph2:
        for insn1 in flowgraph1:
            if (insn1.getDefVar() in insn2.getUseVars()
            and (insn2 not in flowgraph1[insn1])):
                flowgraph1[insn1].append(insn2)

            if (insn2.getDefVar() in insn1.getUseVars()
            and (insn1 not in flowgraph2[insn2])):
                flowgraph2[insn2].append(insn1)
    
    flowgraph1.update(flowgraph2)


# return True if block1 is a precessor of block2
def isPred(block1, block2):
    currBBs = list()
    depBBs = list()
    currBBs.extend(block1.next_bbs)

    # we find all the dependent basic blocks
    while len(currBBs) != 0:
        cur_bb = currBBs.pop()
        depBBs.append(cur_bb)

        for next_bb in cur_bb.next_bbs:
            if (next_bb not in currBBs 
            and next_bb not in depBBs):
                currBBs.append(next_bb)

    if block2 in depBBs:
        return True
    else:
        return False


def distanceFromIdx(index1, index2):
    # skip if the graph matching will be too slow
    if len(index1) > 10 or len(index2) > 10:
        return 100 
    
    graph1 = to_nx_graph(index1)
    graph2 = to_nx_graph(index2)
    return nx.algorithms.similarity.graph_edit_distance(graph1, graph2, node_subst_cost=node_sub_cost, node_del_cost=node_del_cost, node_ins_cost=node_ins_cost)





def doMatching(store_index, load_index):
    matched = []

    for storeInsnssa in store_index:
        storeIdx = store_index[storeInsnssa]

        for loadInsnssa in load_index:
            loadIdx = load_index[loadInsnssa]

            dis = distanceFromIdx(storeIdx, loadIdx)

            if dis == 0:
                matched.append([storeInsnssa, loadInsnssa])
                
    return matched


def condOp_to_sign(condOp, has_two_iszero):
    if condOp not in evmAnalysis.CONDITIONAL_CHECK:
        return ""
    if has_two_iszero:
        if condOp == "LT":
            return " >= "
        elif condOp == "GT":
            return " <= "
        elif condOp == "EQ":
            return " != "  
    else:
        if condOp == "LT":
            return " < "
        elif condOp == "GT":
            return " > "
        elif condOp == "EQ":
            return " = "  

def isTP(ssa):
    if isinstance(ssa, SSA) and ssa.method_name in evmAnalysis.SPECIAL_VARIABLES:
        return True
    return False



    # this function extracts all the variables (in the given list) that are used in a conditional check instruction or a call or a memory/storage store
def getConditionalCheckOrCallOrStoreVars(ssalist):
    condVars = list()
    callArgs = list()
    storeVars = {}

    for ssa in ssalist:
        if (ssa.method_name in evmAnalysis.CONDITIONAL_CHECK):
            condlist = list()
            condlist.extend(ssa.getUseVars())
            condlist.append(ssa)
            condVars.append(condlist)
        #elif (insn.method_name == "CALL"):
        elif ssa.getInst().is_call:
            callArgs.extend(ssa.getUseVars())
        elif (ssa.method_name == "MSTORE" or ssa.method_name == "SSTORE" or ssa.method_name == "MSTORE8"):
            # keep track of offset
            storeVars[ssa] = ssa.getUseVars()[0]
            # storeVars.extend(insn.getUseVars()[0])
    return condVars, callArgs, storeVars


    # check if a var in varSet is defined by methodName. If so, we find the offset
def findMethodInSet(insnSet, methodName):
    if isinstance(methodName, str):
        for ssa in insnSet:
            if ssa.method_name == methodName:
                return ssa
    elif isinstance(methodName, list):
        for mn in methodName:
            for ssa in insnSet:
                if ssa.method_name == mn:
                    return ssa
    return None