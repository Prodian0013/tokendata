from web3 import Web3


class Holder(object):
    def __init__(self, address, balance, block, timestamp) -> None:
        self.address = address
        self.balance = int(balance)
        self.converted_balance = 0
        self.staked_balance = 0
        self.staked_balance_converted = 0
        self.block = block
        self.timestamp = timestamp

        # Convert balance to double
        self.convert_balance()

    def convert_balance(self):
        self.converted_balance =  "{:.9f}".format(Web3.fromWei(int(self.balance), 'gwei'))