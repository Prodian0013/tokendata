from app.models.transaction_count import Transaction_Count
from app.utils.elastic import ElasticsearchManager
from app.utils.utils import get_data
from datetime import datetime


primer = [
    {"$match": {"log_events": {"$elemmatch": {"decoded.name": "Transfer"}}}},
    {
        "$group": {
            "_id": {
                "month": {"$month": "block_signed_at"},
                "day": {"$dayOfMonth": "block_signed_at"},
                "year": {"$year": "block_signed_at"},
                "hour": {"$hourOfDay": "block_signed_at"},
            },
            "transfer_count": {"$sum": 1},
        }
    },
]


class TransactionScanner:
    def __init__(self, api_key, contract_address) -> None:
        self.api_key = api_key
        
        self.uri = (
            "https://api.covalenthq.com/v1/43114/address/"
            + contract_address
            + "/transactions_v2/?page-size=10000&primer="
            + str(primer)
            + "&key="
            + self.api_key
        )
        self._es = ElasticsearchManager()

    def process(self):
        data = get_data(self.uri)
        if "data" in data and "items" in data["data"]:
            transfers = data["data"]["items"]
            for t in transfers:
                trans = Transaction_Count(
                    datetime(
                        t["id"]["year"],
                        t["id"]["month"],
                        t["id"]["day"],
                        t["id"]["hour"],
                    ),
                    t["transfer_count"],
                )
                print(trans.__dict__)
