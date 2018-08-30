# ethereum event log collector and parser
A native light-weight implementation of log collector and parser for ethereum event logs. 

## how to install?
```
pip install eth_log
```

## how to use?

Quick start

```
from eth_log.helpers.eventlog_helper import collect_event_logs_by_contract_address

# smart contract address you would like to collect logs for (e.g. CryptoKitties Core)
smart_contract_address = '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d'

# your etherscan api key
etherscan_api_key = 'YourApiKeyToken'

# collect event logs from block number 
from_block_num = 6230000

# collect event logs to block number (included)
to_block_num = 6235800

# output path for csv files for events
output_csv_files_path = '/ck-core-events/'


collect_event_logs_by_contract_address(smart_contract_address,
									   etherscan_api_key,
									   from_block_num,
									   to_block_num,
									   output_csv_files_path)


```

You can instead use components individually... 

```
import eth_log
from eth_log.models.contract import Contract
from eth_log.models.eventlog import EventLog

# making contract ready to detect topics of this smart contract and 
# be able to process evenlogs
contract = Contract(<contract_address>, <contract_abi_string>)

# create an eventlog
event_log = EventLog(<contract_address>,
	                 <topic_fingerprints>,
	                 <log_hex_str_data>,
	                 <block_number>,
	                 <log_index>,
	                 <tx_hash>,
	                 <tx_index>)

# add to to the contract to be processed
contract.add_eventlog(event_log)

# check processed eventlogs
contract.eventlogs


```

Check out `eth_log/example.py`. This will give you better understanding on how to use this package to collect and process event logs for an smart contract.
