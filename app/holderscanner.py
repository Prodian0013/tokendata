import asyncio
from asyncio.locks import Semaphore
from concurrent.futures import ThreadPoolExecutor
import json
from app.utils.constants import (HOLDER_URI, BLOCK_URI, STAKED_INDEX, HOLDER_INDEX, EXEMPT_ADDRESSES)
from app.utils.elastic import ElasticsearchManager
from app.models.block import Block
from app.models.holder import Holder
from app.utils.utils import generate_block_ranges, get_data
from app.models.contract import ContractConnector
from typing import List, Tuple
from web3 import Web3
from datetime import datetime


class PotentialStakedHolders():
    def __init__(self) -> None:
        self.holders = []

    def read(self):
        try:
            with open('potential_staked_holders.json') as f:
                self.holders = json.load(f)
        except FileNotFoundError:
            self.holders = []

    def write(self):

        if len(self.holders) > 0:
            try:
                with open('potential_staked_holders.json', 'w') as f:
                    json.dump(self.holders, f)
            except Exception as exc:
                print("Exception: Unable to write potential_staked_holders.json " + str(exc))


class HolderScanner():
    def __init__(self, api_key, start_block, end_block, block_range, staked_contract_address, contract_address, latest) -> None:
        self.api_key = api_key
        self.start_block = start_block
        self.end_block = end_block
        self.uri = None
        self.current_block = None
        self._es = ElasticsearchManager()
        self.latest = latest
        self.holder_contract = ContractConnector(contract_address)
        self.staked_contract = ContractConnector(staked_contract_address)
        self.block_range = block_range

        if self.end_block == 'latest':
            self.end_block = self.holder_contract.get_latest_block_number()


    def create_uri(self, block_number):
        uri = HOLDER_URI \
            + "/" + self.holder_contract.contract_address \
            + "/token_holders/?quote-currency=USD&format=JSON"
        if not self.latest:
            uri = uri + "&block-height=" + str(block_number)
        return uri + "&key=" + self.api_key + "&page-size=10000"

    def get_staked_balance(self, wallet_address, block_number) -> Tuple:
        converted_balance = 0
        balance = 0
        try:
            balance = self.staked_contract.contract.functions.balanceOf(self.staked_contract.web3.toChecksumAddress(wallet_address)).call(block_identifier=block_number)
        except Exception as exc:
            # print("Exception: " + str(wallet_address) + " at block "+ str(block_number) + " " + str(exc))
            balance = 0
        if balance > 0:
            converted_balance = "{:.9f}".format(Web3.fromWei(int(balance), 'gwei'))
        return balance, converted_balance

    def get_timestamp(self, block_height):
        uri = "{}/{}/?quote-currency=USD&format=JSON&key={}".format(BLOCK_URI, block_height, self.api_key)        
        data = get_data(uri)
        if "data" in data and "items" in data["data"]:
            return data["data"]["items"][0]["signed_at"]

    async def gather_holders(self, semaphore: Semaphore, block_number, is_staked: bool=False):
        await semaphore.acquire()
        loop = asyncio.get_event_loop()
        print("processing " + str(block_number))
        timestamp = await loop.run_in_executor(ThreadPoolExecutor(50), self.get_timestamp, block_number)  # type: datetime
        print("Block " + str(block_number) + " timestamp: " + str(timestamp))
        holders = [] # type: List[Holder]
        index = HOLDER_INDEX
        if is_staked:
            index = STAKED_INDEX
        if self.latest:
            index = index + "_latest"
        print("Block " + str(block_number) + " getting holders")
        data = await loop.run_in_executor(ThreadPoolExecutor(50), get_data, self.create_uri(block_number))
        print("Block " + str(block_number) + " processing holder data")
        if "data" in data and "items" in data["data"]:
            cov_holders = data["data"]["items"]
            psh = PotentialStakedHolders()
            psh.read()
            for h in cov_holders:
                holder = Holder(h["address"], h["balance"], block_number, timestamp) # type: Holder
                if holder.address not in psh.holders:
                    psh.holders.append(holder.address)
                holders.append(holder)
            psh.write()

        print("Block " + str(block_number) + ": Getting potential staked holders")
        combined_holders = []
        for h in psh.holders:
            holder = next((x for x in holders if x.address == h), None)
            if not holder:
                holder = Holder(h, 0, block_number, timestamp) # type: Holder
            if holder.address not in EXEMPT_ADDRESSES:
                staked_balance, staked_balance_converted = await loop.run_in_executor(ThreadPoolExecutor(50), self.get_staked_balance, holder.address, block_number)
                holder.staked_balance = staked_balance
                holder.staked_balance_converted = staked_balance_converted
                if holder.staked_balance > 0 or holder.balance > 0:                                    
                    combined_holders.append(holder.__dict__)
        
        print("Block " + str(block_number) + ": Sending data to elastic")
        if len(combined_holders) > 0:
            if is_staked:
                print(str(len(combined_holders)) + " sFort holders sent to elastic")
            else:
                print(str(len(combined_holders)) + " Fort holders sent to elastic " + index)
            self._es._bulk(combined_holders, index)
        semaphore.release()


    def start_mapping(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._get_holders())


    async def _get_holders(self):
        mySemaphore = asyncio.Semaphore(value=5)
        tasks = []
        for start_from_block, end_at_block in generate_block_ranges(self.start_block, self.end_block, self.block_range):
            if start_from_block > end_at_block:
                continue

            print('Gather holders at block %s' % (start_from_block))
            #self.current_block = Block(height=start_from_block)
            #self.current_block.get_timestamp(api_key=self.api_key)
            tasks.append(self.gather_holders(mySemaphore, start_from_block))
            #self.update_last_scanned()
        await asyncio.wait(tasks)

    def update_last_scanned(self):
        with open('state.json', 'w') as fp:
            print(json.dumps({ "last_scanned_block": self.current_block.height}), file=fp)

    def get_last_scanned(self):
        data = None
        try:
            with open('state.json') as fp:
                data = json.load(fp)
        except Exception as exc:
            print(str(exc))

        if data and "last_scanned_block" in data and data["last_scanned_block"] > 0:
            self.start_block = data["last_scanned_block"]
