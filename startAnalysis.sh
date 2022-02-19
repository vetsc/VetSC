#bin/bash
EXT=.sol

input=$1
funcNames=$2

OUTPUT_DIR="./output"
SRC_DIR="./src"

rm *dot
rm *pdf

# Example: ./startAnalysis.sh data/solidity-auction/Auction.sol

if [[ $funcNames != *.txt ]];
then
    echo "Second argument is the function name list"
    echo "It has to be a txt file!"
    exit
fi


if [[ $input == *.sol ]];
then
    filename=$(basename $input)
    file_wo_ext=$(basename $filename $EXT)    
    
    echo "compiling the smart contract $filename"
    solc -o $OUTPUT_DIR/$file_wo_ext --overwrite --bin $input
    
    echo "start analysis..."
    python3 $SRC_DIR/evmAnalysis.py --bytecode $OUTPUT_DIR/$file_wo_ext/$file_wo_ext.bin --funcList $funcNames
elif [[ $input == *.bin ]];
then
    python3 $SRC_DIR/evmAnalysis.py --bytecode $input --funcList $funcNames
else
    echo "start analysis by downloading from blockchain..."
    python3 $SRC_DIR/evmAnalysis.py --addr $input --funcList $funcNames
fi


for file in ./*.dot
do 
	filename=$(basename $file .dot)
	dot -Tpdf $file -o $filename.pdf
done
