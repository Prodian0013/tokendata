import json
from app.utils.constants import (HOLDER_URI, BLOCK_URI, STAKED_INDEX, HOLDER_INDEX)
from app.utils.elastic import ElasticsearchManager
from app.models.block import Block
from app.models.holder import Holder
from app.utils.utils import generate_block_ranges, get_data
from app.models.contract import Contract


class HolderScanner():
    def __init__(self, api_key, start_block, end_block, block_range, staked_contract_address, contract_address, latest) -> None:
        self.api_key = api_key        
        self.start_block = start_block
        self.end_block = end_block
        self.uri = None
        self.current_block = None
        self._es = ElasticsearchManager()
        self.latest = latest
        self.holder_contract = Contract(contract_address)
        self.staked_contract = Contract(staked_contract_address)        
        self.block_range = block_range



    def get_latest_block(self):         
        data = get_data(BLOCK_URI + "/latest/?quote-currency=USD&format=JSON&key=" +  self.api_key) 
        self.start_block = data["data"]["items"][0]["height"]
        self.end_block = self.start_block + self.block_range        

    def holder_uri(self, contract_address: str) -> str:
        self.uri = HOLDER_URI \
            + "/" + contract_address \
            + "/token_holders/?quote-currency=USD&format=JSON"
        if not self.latest:
            self.uri = self.uri + "&block-height=" + str(self.current_block.height)
        self.uri = self.uri + "&key=" + self.api_key + "&page-size=10000"

    def get_staked_balance(self, wallet_address):
        return self.staked_contract.functions.balanceOf(web3.toChecksumAddress(wallet_address)).call(block_identifier=self.current_block.height)

    def gather_holders(self, is_staked: bool=False):    
        holders_dict = []
        index = HOLDER_INDEX
        if is_staked:
            index = STAKED_INDEX
        if self.latest:
            index = index + "_latest"
        data = get_data(self.uri)        
        if "data" in data and "items" in data["data"]:    
            holders = data["data"]["items"]
            for h in holders:
                staked_balance = self.get_staked_balance(h["address"])            
                holder = Holder(h["address"], h["balance"], staked_balance, self.current_block.height, self.current_block.timestamp) # type: Holder
                holders_dict.append(holder.__dict__)
        
        if len(holders_dict) > 0:
            if is_staked:
                print(str(len(holders_dict)) + " sFort holders sent to elastic")
            else:                
                print(str(len(holders_dict)) + " Fort holders sent to elastic " + index)
            self._es._bulk(holders_dict, index)
        
    def get_holders(self):
        for start_from_block, end_at_block in generate_block_ranges(self.start_block, self.end_block, self.block_range):
            if start_from_block > end_at_block:
                continue
            
            print('Gather holders at block %s' % (start_from_block))
            self.current_block = Block(height=start_from_block)
            self.current_block.get_timestamp()
            self.holder_uri(self.holder_contract.address)
            self.gather_holders()
            #self.holder_uri(STAKED_CONTRACT)
            #self.gather_holders(is_staked=True)
            self.update_last_scanned()

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