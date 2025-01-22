# Experiments Figure Plotting Code
## Authors
Saeed Ranjbar Alvar, Mohammad Akbari, David (Ming Xuan) Yue, Yong Zhang

Huawei Technologies Canada Co., Ltd,
Vancouver, Canada

## Dependencies
Python: 3.8.15 or higher

web3.py: https://github.com/ethereum/web3.py

hardhat: https://hardhat.org/

matplotlib: https://matplotlib.org/stable/index.html#

numpy: https://numpy.org/

pycryptodome: https://github.com/Legrandin/pycryptodome

## Running the code
Each of the scripts in the `plots/` directory will produce the results related to the blockchain experiment found in the paper. 

All of these scripts require an Ethereum node. Easiest way to set this up is to
use a local node provided by Hardhat. You can also use your own Ethereum node or 
a Ethereum Test Network, however, you will need to change the hardcoded Ethereum 
endpoint in the scripts. After installing all the dependencies, you can boot one 
up using:

```
$ npx hardhat node
```
The `plots/batchmint_gas_plot.py` plots how much gas is needed to mint a certain
number of assets (Figure 3)

The `plots/gas_method.py` plots how much gas is needed to deploy each contract
and how much gas each smart contract method costs (Table 1. top )

The `plots/registration_trade_plot.py` plots how much gas is needed for each
stage of the market. (Table 1 bottom)

The `plots/contract_local.py` is a wrapper over the web3.py library and used
by every other script. 

The `contracts/` directory contains all the smart contracts used by our market.
The scripts will automatically deploy these contracts when you run them, however
you still need to compile these smart contracts. Compile them using

```
$ npx hardhat compile
```

Hardhat should automatically detect where the contracts are located and produce an 
`artifacts/` directory. Do not modify the layout of this directory, the scripts
are expecting the default layout.