This directory contains some important artifacts for Opensea.io, which is one of the largest marketplaces for NFTs.



1. HUXLEY Comic_ Issue 2 - First Edition #5,091 - HUXLEY Comics _ OpenSea.jpg
This is a screenshot of an item that is on sale. Users can interact with the underlying smart contract by clicking the UI button 'place bid'. 
Once clicked, it will initiate a call to the function atomicMatch_() in the contract at 0x7be8076f4ea4a4ad08075c2508e481d6c946d12b.

2. WyvernExchange.sol
This is the source code of the underlying smart contract, which implements the actual Dutch auction business logic for Opensea.

3. dutch_auction_bmg.pdf
This is a business model graph (partial) to showcase how our technique can characterize the Dutch auction business logic for Opensea.
