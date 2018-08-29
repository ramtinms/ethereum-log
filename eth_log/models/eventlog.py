from datetime import datetime
import pandas as pd

class EventLog:

    def __init__(self, contract_address,
                       topic_fingerprints,
                       log_hex_str_data,
                       block_number,
                       log_index,
                       tx_hash,
                       tx_index,
                       timestamp=None, 
                       gas_price=None,
                       gas_used=None):
        self.contract_address = contract_address
        self.topic_fingerprints = topic_fingerprints
        self.log_hex_str_data = log_hex_str_data
        self.block_number = block_number
        self.log_index = log_index
        self.timestamp = timestamp
        self.gas_price = gas_price
        self.gas_used = gas_used
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        # will be used later after processing
        self.event_name = None
        self.data = None

    def get_dataframe(self):
        new_dict = {}
        for key, value in self.__dict__.items():
            if key != 'data':
                new_dict[key] = value
            else:
                for item in value:
                    new_dict['data_{}'.format(item.get('name'))] = item.get('value')
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
    def from_etherscan_json(cls, json_obj):
        return cls(**{'contract_address': json_obj.get('address'),
         'topic_fingerprints': json_obj.get('topics'),
         'log_hex_str_data': json_obj.get('data'),
         'block_number': cls.process_number(json_obj.get('blockNumber')),
         'log_index': cls.process_number(json_obj.get('logIndex')),
         'gas_price': cls.process_number(json_obj.get('gasPrice')),
         'gas_used': cls.process_number(json_obj.get('gasUsed')),
         'tx_hash': json_obj.get('transactionHash'),
         'tx_index': cls.process_number(json_obj.get('transactionIndex')),
         'timestamp': cls.process_timestamp(json_obj.get('timeStamp')),
        })
