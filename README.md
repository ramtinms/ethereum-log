# Ethereum event log parser
A light-weight implementation of log aggregator and parser for ethereum event logs. 

[![Build Status](https://travis-ci.com/ramtinms/ethereum-log.svg?branch=master)](https://travis-ci.com/ramtinms/ethereum-log)

## how to install?
```
pip install eth_log
```

## How to use this?
### Setup Contract 
Create a contract object by passing smart contract address and contract ABI string.
```python
from eth_log.models.contract import Contract

contract_address = "0x06012c8cf97bead5deae237070f9587f8e7a266d"
contract_abi_string = "[{"constant":true,"inputs":[{"name":"_interfaceID","type":"bytes4"}], ... "
contract = Contract(contract_address, contract_abi_string)
```

#### what if I don't have ABI ?
You might be able to collect it from etherscan, for which this package provides a handler for etherscan API.
```python
from eth_log.handlers.etherscan_api_handler import EtherscanAPIHandler

handler = EtherscanAPIHandler('YourApiKeyToken')
contract_abi_string = handler.fetch_contract_abi_string(contract_address)
contract = Contract(contract_address, contract_abi_string)
```

### Get topics
After creating the contract object you can ask for list of topics, you can also pick a topic by name of Event.
```python
for topic in contract.get_topics():
    print(topic.fingerprint, topic.description)
    
birth_topic = contract.get_topic_by_event_name('Birth')
```

### Collect event logs for specific topic
This package provides different handlers to collect log events, you can ether use Etherscan API or Infura API or google Bigquery API.
```python
bq_hander = GoogleBigqueryHandler()
min_block_number = 6230000
max_block_number = 6235800
eventlogs = bq_hander.fetch_eventlogs_by_topic(contract_address, birth_topic,
                                               min_block_number=min_block_number,
                                               max_block_number=max_block_number,
                                               parsing=True)
```
This will fetch logs from google bigquery and apply log parser (birth topic) to the logs. 

instead of block range you can also use timestamp 
```python
from datetime import datetime 

min_block_timestamp = datetime(2018, 9, 28)
max_block_timestamp = datetime(2018, 9, 29)

eventlogs = bq_hander.fetch_eventlogs_by_topic(contract_address, birth_topic,
                                               min_block_timestamp=min_block_timestamp,
                                               max_block_timestamp=max_block_timestamp,
                                               parsing=True)
print(len(eventlogs))
print(eventlogs[0])
```

You can also convert these logs into a dataframe using ...
```python
# convert to pandas dataframe 
def convert_to_dataframe(list_of_eventlogs):
    return pd.DataFrame([evenlog.to_pandas() for evenlog in list_of_eventlogs])

df = convert_to_dataframe(eventlogs)
print(df.describe())
print(df.dtypes)
```
