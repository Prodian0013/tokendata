from app.utils.constants import BLOCK_URI
from app.utils.utils import get_data


class Block(object):
    def __init__(self, height) -> None:
        self.height = height
        self.timestamp = None

    def get_timestamp(self, api_key):
        uri = "{}/{}/?quote-currency=USD&format=JSON&key={}".format(BLOCK_URI, self.height, api_key)
        data = get_data(uri)        
        if "data" in data and "items" in data["data"]: 
            self.timestamp = data["data"]["items"][0]["signed_at"]