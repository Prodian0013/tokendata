# Token Holders
Pull token holders from web3 on avalanche.

## Required Dependencies
1. Local Elasticsearch setup
2. Covalenthq Api Key

## Install python dependencies 
```bash
pip3 install -r requirements.txt
```

## Usage
```
python3 run.py -h

usage: run.py [-h] [--get-holders] [--get-transaction-counts] [--latest] [--staked-address STAKED_CONTRACT_ADDRESS] [--contract-address CONTRACT_ADDRESS] [--start STARTING_BLOCK] [--end ENDING_BLOCK]
              [--block-range BLOCK_RANGE] [--api-key API_KEY]

optional arguments:
  -h, --help            show this help message and exit
  --get-holders         Get holders by block id
  --get-transaction-counts
                        Get transactions count
  --latest              Get latest block
  --staked-address STAKED_CONTRACT_ADDRESS
                        Staked Contract Address
  --contract-address CONTRACT_ADDRESS
                        Contract Address
  --start STARTING_BLOCK
                        Starting block
  --end ENDING_BLOCK    Ending Block
  --block-range BLOCK_RANGE
                        Block range
  --api-key API_KEY     Covalenthq api key
