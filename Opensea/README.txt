This directory contains some important artifacts for Opensea.io, which is one of the largest marketplaces for NFTs.

Opensea.io implements a Dutch auction business logic. 
At a Dutch auction, the seller starts with a high selling price and then lowers it until there is a bid for the item, or it reaches a reserve price.
Therefore, at any moment, the current selling price is calculated by subtracting a timing-related diff amount from the seller starting price. 



1. Croc #4867 - Acrocalypse _ OpenSea.jpg
This is a screenshot of an item on sale, named Croc #4867. Users can interact with the underlying smart contract by clicking the UI button 'place bid'. 
Once clicked, it will initiate a call to the function atomicMatch_() in the contract at 0x7be8076f4ea4a4ad08075c2508e481d6c946d12b.
Given the very vague function name (atomicMatch), manual semantic inference, which is required by state-of-the-art techniques such as VerX, can be very hard.
Yet, our technique can automatically infer that the function is for bidding an auction.


2. WyvernExchange.sol
This is the source code of the underlying smart contract, in which the actual Dutch auction business logic is implemented.


3. spec.pdf
This file contains the LTL spec for Dutch auction bidding process.


4. dutch_auction_bmg.pdf
This is a business model graph (BMG) to showcase how our technique characterizes the Dutch auction business logic for Opensea.
Based on the spec for Dutch auction bidding process and the generated BMG, our technique can infer the following semantics for program variables.

sellPrice   -->     current sell price
buyPrice    -->     current bid
sell.maker  -->     auction owner

Finally, our model checking can perform safety vetting for the two safety rules.
