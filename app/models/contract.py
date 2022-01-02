from web3 import HTTPProvider, Web3
from web3.eth import Contract
from web3.middleware import geth_poa_middleware
import requests
import json

RPC_URI = 'https://api.avax.network/ext/bc/C/rpc'
ABI_URI = 'https://api.snowtrace.io/api?module=contract&action=getabi&address='

class Contract():
    def __init__(self) -> None:
        self.web3 = Web3(HTTPProvider(RPC_URI)) # type: Web3
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        address = self.web3.toChecksumAddress(self.staked_contract_address)
        abi = self.fetch_abi(address)
        self.contract = self.web3.eth.contract(abi=abi, address=address)

    def fetch_abi(address) -> list:
        response = requests.get('%s%s'%(ABI_URI, address))
        response_json = response.json()
        abi = json.loads(response_json['result']) # type: list
        return abi