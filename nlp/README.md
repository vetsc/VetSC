# Semantic Dapp Web analysis

auction_str = ("bid cancel finalize" ,"auction")
voting_str = ("vote", "vote")
wallet_str = ("deposit withdraw transfer", "wallet")
gambling_str = ("buy refund draw", "gambling")
trading_str = ("buy sell", "trade")
gambling_dice_str = ("roll", "gambling/dice")
crowdsale_str = ("invest refund close", "crowdsale")

## How to run

1. Prepare [glove](https://nlp.stanford.edu/projects/glove/) vectors in your local environment. (We use the `glove.6B.300d.txt`)
2. run the `run.ipynb`