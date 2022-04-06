This directory contains some important artifacts for LooksRare, which is one of the largest marketplaces for NFTs. 



1. UI.jpg
This is a screenshot of an item on sale. Users can interact with the underlying smart contract by clicking the UI button 'Buy Now'. 
Once clicked, it will initiate a call to the function matchAskWithTakerBid() in the contract at 0x59728544b08ab483533076417fbbb2fd0b17ce3a.


2. spec
LooksRare implements a trading business logic, whose spec is presented in Table 7 in the paper.


3. bmg.pdf
This is a business model graph (BMG) to showcase how our technique works in trading 'buy' logic for LooksRare.
Based on the trading spec and the generated BMG, our technique can infer the following semantics for program variables.

CALLDATA.askPrice			-->	sell price
CALLDATA.maker			-->	owner
isUserOrderNonceExecuted	-->	sale.active

Finally, our model checking can perform safety vetting for the two safety rules.
