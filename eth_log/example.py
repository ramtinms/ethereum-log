from eth_log.models.contract import Contract
from eth_log.handlers.etherscan_api_handler import EtherscanAPIHandler
from eth_log.handlers.infura_api_handler import InfuraAPIHandler
from eth_log.handlers.google_bigquery_handler import GoogleBigqueryHandler


handler = EtherscanAPIHandler('YourApiKeyToken')
# CryptoKitties Core contract
contract_address = '0x06012c8cf97BEaD5deAe237070F9587f8E7A266d'
contract_abi_string = handler.fetch_contract_abi_string(contract_address)
contract = Contract(contract_address, contract_abi_string)

print('-------------------------------------')
print('this contract can parse these topics:')
for item in contract.topic_parsers:
	print(item)
print('-------------------------------------')

# fetch eventlogs from block 6230000 to block 6235800 (included)
min_block_number = 6230000
max_block_number = 6235800
# handler.fetch_eventlogs_by_contract(contract, min_block_number, max_block_number)

# handler2 = InfuraAPIHandler(verbose=True)
# handler2.fetch_eventlogs_by_contract(contract, min_block_number, max_block_number)

handler3 = GoogleBigqueryHandler(verbose=True)
handler3.fetch_event_logs(contract, min_block_number, max_block_number)

# dump_file = 'data/eth_logs/all'
# handler3.fetch_eventlogs_by_contract_from_file(dump_file, contract, min_block_number, max_block_number)

print('-------------------------------------')
print('this contract has {} type of eventlogs'.format(len(contract.eventlogs)))
print('total logevents : {}'.format(contract.total_eventlogs))
print('writing eventlogs to csv')
output_directory_path = 'data/ck_core_events3/'
contract.export_eventlogs_to_csv_files(output_directory_path, index=False)
print('-------------------------------------')






