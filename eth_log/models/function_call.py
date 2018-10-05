from datetime import datetime
import pandas as pd


class FunctionCall:

    def __init__(self, contract_address,
    				   caller,
                       data,
                       block_number,
                       tx_hash,
                       tx_index,
                       nonce,
                       gas,
                       receipt_status=None, 
                       receipt_root=None,
                       block_hash=None,
                       timestamp=None, 
                       gas_price=None,
                       gas_used=None):
        self.contract_address = contract_address
        self.caller = caller
        self.data = data
        self.block_number = block_number
        self.block_hash = block_hash
        self.timestamp = timestamp
        self.gas = gas
        self.gas_price = gas_price
        self.gas_used = gas_used
        self.receipt_status = receipt_status
        self.receipt_root = receipt_root
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.nonce = nonce
        # will be used later after processing
        self.function_name = None
        self.input_data = None
        self.eventlogs = []

    def __str__(self):
        template = "timestamp: {timestamp} \n"
        template += "contract_address: {contract_address} \n"
        template += "function_name: {function_name} \n"
        new_dict = {}
        for key, value in self.__dict__.items():
            if key == 'input_data':
                for item in value:
                    new_dict['input_data_{}'.format(item.get('name'))] = item.get('value')
                    template += "{}: {{input_data_{}}}\n".format(item.get('name'), item.get('name'))
            elif key == 'timestamp':
                 new_dict['timestamp'] = self.timestamp.isoformat()
            elif key == "event_name":
                 new_dict['function_name'] = value
            elif value is not None:
                template += "{}: {{{}}}\n".format(key, key)
                new_dict[key] = value
        return template.format(**new_dict)

    def to_pandas(self):
        new_dict = {}
        for key, value in self.__dict__.items():
            if key == 'data':
                for item in value:
                    new_dict['data_{}'.format(item.get('name'))] = item.get('value')
            else:
                new_dict[key] = value
        return pd.Series(new_dict)

    @classmethod
    def process_number(cls, inp):
        if inp.startswith('0x'):
            inp = inp[2:]
        if inp:
            return int(inp, 16)
        else:
            return 0

    @classmethod
    def process_timestamp(cls, inp):
        if inp.startswith('0x'):
            inp = inp[2:]
        return datetime.utcfromtimestamp(int(inp, 16))

    @classmethod
    def from_google_public_dataset_json(cls, json_obj):
        return cls(**{'contract_address': str(json_obj.get('to_address')),
         'caller': json_obj.get('from_address'),
         'data': json_obj.get('input'),
         'block_hash': json_obj.get('block_hash'),
         'block_number': int(json_obj.get('block_number')),
         'nonce': json_obj.get('nonce'),
         'gas': json_obj.get('gas'),
         'gas_price': json_obj.get('gas_price'),
         'gas_used': json_obj.get('receipt_gas_used'),
         'receipt_status': int(json_obj.get('receipt_status')), 
         'receipt_root': json_obj.get('receipt_root'),
         'tx_hash': json_obj.get('hash'),
         'tx_index': int(json_obj.get('transaction_index')),
         'timestamp': json_obj.get('block_timestamp')
        })

