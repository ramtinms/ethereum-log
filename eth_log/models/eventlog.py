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
                       block_hash=None,
                       timestamp=None, 
                       gas_price=None,
                       gas_used=None):
        self.contract_address = contract_address
        self.topic_fingerprints = topic_fingerprints
        self.log_hex_str_data = log_hex_str_data
        self.block_number = block_number
        self.block_hash = block_hash
        self.log_index = log_index
        self.timestamp = timestamp
        self.gas_price = gas_price
        self.gas_used = gas_used
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        # will be used later after processing
        self.event_name = None
        self.data = None

    def __str__(self):
        template = "timestamp: {timestamp} \n"
        template += "contract_address: {contract_address} \n"
        template += "topics: {topics} \n"
        template += "event: {event} \n"
        new_dict = {}
        for key, value in self.__dict__.items():
            if key == 'data':
                for item in value:
                    new_dict['data_{}'.format(item.get('name'))] = item.get('value')
                    template += "{}: {{data_{}}}\n".format(item.get('name'), item.get('name'))
            elif key == 'timestamp':
                 new_dict['timestamp'] = self.timestamp.isoformat()
            elif key == "event_name":
                 new_dict['event'] = value
            elif key == 'topic_fingerprints':
                new_dict['topics'] = ', '.join(self.topic_fingerprints)
            elif value:
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

    @classmethod
    def from_infura_json(cls, json_obj):
        return cls(**{'contract_address': json_obj.get('address'),
         'topic_fingerprints': json_obj.get('topics'),
         'log_hex_str_data': json_obj.get('data'),
         'block_hash': json_obj.get('blockHash'),
         'block_number': cls.process_number(json_obj.get('blockNumber')),
         'log_index': cls.process_number(json_obj.get('logIndex')),
         'tx_hash': json_obj.get('transactionHash'),
         'tx_index': cls.process_number(json_obj.get('transactionIndex'))
        })
        
    @classmethod
    def from_google_public_dataset_json(cls, json_obj):
        return cls(**{'contract_address': str(json_obj.get('address')),
         'topic_fingerprints': json_obj.get('topics'),
         'log_hex_str_data': json_obj.get('data'),
         'block_hash': json_obj.get('block_hash'),
         'block_number': int(json_obj.get('block_number')),
         'log_index': int(json_obj.get('log_index')), 
         'tx_hash': json_obj.get('transaction_hash'),
         'tx_index': int(json_obj.get('transaction_index')),
         'timestamp': json_obj.get('block_timestamp')
        })
