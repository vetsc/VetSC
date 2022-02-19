import os
import sys
import networkx as nx

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from octopus.arch.evm.model import Model
from octopus.arch.evm.model import SPECIAL_VARIABLES

from octopus.platforms.ETH.cfg import EthereumCFG
from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_MAINNET

import evmAnalysis
import modelGeneration
import myUtility

from octopus.core.ssa import SSA


evm_bytecode_contract = "../output/contract.bytecode"



def downloadBytecode(address):
    # delete any existing bytecode file
    prev_bytecode_exists = os.path.isfile(evm_bytecode_contract)
    if prev_bytecode_exists:
        os.remove(evm_bytecode_contract)

    KEY_API = "bHuaQhX91nkQBac8Wtgj"
    # connection to ROPSTEN network (testnet)
    # explorer = EthereumInfuraExplorer(KEY_API, network=INFURA_MAINNET)

    # connection to MAINNET network (mainnet)
    explorer = EthereumInfuraExplorer(KEY_API)

    # Test ROPSTEN network current block number
    # block_number = explorer.eth_blockNumber()
    # print(block_number)

    # Retrieve code of this smart contract
    addr = address #"0xa0388ffb2A3c198DeE723135E0cAa423840b375A"
    #addr = "0x7ac337474ca82e0f324fbbe8493f175e0f681188"
    print("Downloading smart contract...")
    code = explorer.eth_getCode(addr)


    print("Storing code into file...")
    with open(evm_bytecode_contract, "w") as f:
        f.write(code)
        f.close()



def startAnalysis(evmAnalysis):
    # 1. we perform backward dataflow analysis on memory and storage operations
    evmAnalysis.trackMemStorageOps()
    # 2. then we try to match them to link up the missing dataflow
    evmAnalysis.linkDataFlow()

    # 3. find entities 
    print("Analysing all tps in the whole smart contract")
    evmAnalysis.specialVarTracking("*", "*")

    # 4. identify entities' value, condition
    evmAnalysis.getConstEntities()

    for entity_ssa in evmAnalysis.entityToFuncHashes:
        # focus on store only. three possible sources: const, tp, and other entity
        if entity_ssa in evmAnalysis.sstore_idxgraph:
            value = evmAnalysis.retrieveValueFromStore(entity_ssa)

            # then try to find precedessor basic block and find condition
            # we only care if the condition involves tp, entity and const
            # tp has been taken care by checkDepBBsForSstore

            
def main():
    # process argument
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, conflict_handler='resolve')
    parser.add_argument('--bytecode', required=False, help='Input bytecode smart contract file')
    parser.add_argument('--addr', required=False, help='Download bytecode from blockchain')
    args = parser.parse_args()

    bytecodeFile = args.bytecode
    address = args.addr

    if not bytecodeFile and not address:
        print("need either bytecode file or addr of the smart contract")
        sys.exit()
    
    if not bytecodeFile:
        downloadBytecode(address)
    else:
        evm_bytecode_contract = bytecodeFile


    # read bytecode smart contract file
    with open(evm_bytecode_contract) as f:
        bytecode_hex = f.read()

    if len(bytecode_hex) == 0:
        print("input bin file: ", evm_bytecode_contract, "is empty! Please check again.")
        sys.exit()

    # generate model for dataflow analysis
    model = Model(bytecode_hex)
    
    # model.cfg.visualize()
    model.findDefUseChain()


    ea = evmAnalysis.EvmAnalysis(model)

    # start analysis
    startAnalysis(ea)
    # constractName = os.path.splitext(os.path.basename(evm_bytecode_contract))[0]

    


if __name__ == "__main__":
    main()