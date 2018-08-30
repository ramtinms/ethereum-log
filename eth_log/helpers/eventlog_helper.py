from eth_log.models.contract import Contract
from eth_log.handlers.etherscan_api_handler import EtherscanAPIHandler

def collect_event_logs_by_contract_address(contract_address,
	                                       etherscan_api_key,
	                                       from_block_num,
	                                       to_block_num,
	                                       output_csv_files_path):
	handler = EtherscanAPIHandler(etherscan_api_key)
	contract_abi_string = handler.fetch_contract_abi_string(contract_address)
	contract = Contract(contract_address, contract_abi_string)
	handler.fetch_eventlogs_by_contract(contract, from_block_num, to_block_num)
	contract.export_eventlogs_to_csv_files(output_csv_files_path)
	print('{} eventlogs fatched, processed and stored at {}.'.format(contract.total_eventlogs, output_csv_files_path))
