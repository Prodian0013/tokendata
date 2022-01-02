from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tokendata.utils.constants import HOLDER_INDEX, STAKED_INDEX

mapping = {
  "settings": {  
      "number_of_replicas": 0      
    },
  "mappings": {      
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "address": {
          "type": "keyword"
        },
        "balance": {
          "type": "long"
        },
        "converted_balance": {
          "type": "double"
        },
        "staked_balance": {
          "type": "long"
        },
        "staked_converted_balance": {
          "type": "double"
        },
        "block": {
          "type": "long"
        },
        "timestamp": {
          "type": "date",
          "format": "iso8601"
        }
      }    
  }
}


class ElasticsearchManager():
    def __init__(self) -> None:
        self._es = Elasticsearch(["localhost:9200"],
                                use_ssl=False,
                                verify_certs=False,                            
                                scheme="http",
                                timeout=30) # type: Elasticsearch

    def _create_index(self, latest: bool=False):
      if latest:        
        #self._es.indices.delete(index=STAKED_INDEX + "_latest", ignore=[400,404])
        #self._es.indices.create(index=STAKED_INDEX + "_latest", body=mapping, ignore=400)       
        self._es.indices.delete(index=HOLDER_INDEX + "_latest", ignore=[400,404])
        self._es.indices.create(index=HOLDER_INDEX + "_latest", body=mapping, ignore=400)
      else:
        #self._es.indices.create(index=STAKED_INDEX, body=mapping, ignore=400)
        self._es.indices.create(index=HOLDER_INDEX,  body=mapping, ignore=400)

    def _bulk(self, holders, index) -> None:
        bulk(self._es, actions=holders, params={'pipeline': 'holders-pipeline'}, index=index)