# ethereum_event_log-parser
A native light weight implementation of log collector and parser for ethereum event logs.

## how to install?
```
pip install eth_log
```

## how to use?

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
