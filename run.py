from app.holderscanner import HolderScanner
import argparse

from app.transaction_counter import TransactionScanner
import os
import sys

API_KEY = "ckey_docs"
STARTING_BLOCK = 7117424
END_BLOCK = "latest"
BLOCK_RANGE = 100
FORT_CONTRACT = "0xf6d46849DB378AE01D93732585BEc2C4480D1fD5" #FORT Token
STAKED_CONTRACT = "0x6b8fb769d1957f2c29abc9d1beb95851cce775d8" # sFORT


parser = argparse.ArgumentParser()
parser.add_argument("--get-holders", help="Get holders by block id", dest='get_holders', action='store_true')
parser.add_argument("--get-transaction-counts", help="Get transactions count", dest='trans_count', action='store_true')
parser.add_argument("--latest", help="Get latest block", dest='latest', action='store_true')
parser.add_argument("--staked-address", help="Staked Contract Address", dest='staked_contract_address', default=STAKED_CONTRACT)
parser.add_argument("--contract-address", help="Contract Address", dest='contract_address', default=FORT_CONTRACT)
parser.add_argument("--start", help="Starting block", dest='starting_block', default=STARTING_BLOCK)
parser.add_argument("--end", help="Ending Block", dest='ending_block', default=END_BLOCK)
parser.add_argument("--block-range", help="Block range", dest='block_range', default=BLOCK_RANGE)
parser.add_argument("--api-key", help="Covalenthq api key", dest='api_key', default=API_KEY)
args, unknown = parser.parse_known_args()

if __name__ == '__main__':
    try:
        if args.get_holders:
            scanner = HolderScanner(api_key=args.api_key, start_block=args.starting_block, end_block=args.ending_block,
                block_range=args.block_range, staked_contract_address=args.staked_contract_address,
                contract_address=args.contract_address, latest=args.latest)
            scanner._es._create_index(args.latest)
            if not args.latest and args.starting_block == STARTING_BLOCK:
                scanner.get_last_scanned()
            if args.latest:
                scanner.get_latest_block()
            scanner.start_mapping()
        if args.trans_count:
            trans_scanner = TransactionScanner(contract_address=args.contract_address, api_key=args.api_key)
            trans_scanner.process()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
