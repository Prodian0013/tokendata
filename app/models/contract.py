from web3 import HTTPProvider, Web3
from web3.eth import Contract
from web3.middleware import geth_poa_middleware
import requests
import json
from typing import Tuple
from web3.eth import Contract

RPC_URI = 'https://api.avax.network/ext/bc/C/rpc'
ABI_URI = 'https://api.snowtrace.io/api?module=contract&action=getabi&address='

class ContractConnector():
    def __init__(self, contract_address) -> None:
        self.contract_address = contract_address
        self.web3 = Web3(HTTPProvider(RPC_URI)) # type: Web3
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.address = self.web3.toChecksumAddress(contract_address)
        self.abi = self.fetch_abi()
        self.contract = self.web3.eth.contract(abi=self.abi, address=self.address) # type: Contract

    def fetch_abi(self) -> list:
        response = requests.get('%s%s'%(ABI_URI, self.contract_address))
        response_json = response.json()
        abi = json.loads(response_json['result']) # type: list
        return abi

    def get_basic_information(self) -> Tuple:
        token_name = self.contract.functions.name().call()
        total_supply = self.contract.functions.totalSupply().call()
        token_symbol = self.contract.functions.symbol().call()
        token_decimal_places = self.contract.functions.decimals().call()

        return token_name, token_symbol, total_supply, token_decimal_places

    def get_latest_block_number(self):
        return self.web3.eth.blockNumber
