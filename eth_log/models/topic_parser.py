from eth_log.utils import split_by_len

class TopicParser:

    def __init__(self, topic):
        self.topic = topic
        self.pad_char_len = 64
        self.char_byte_size = 4 
        self.type_mappings = {
            'uint32': 'uint32',
            'uint8': 'uint8',
            'uint256': 'uint256',
            'bool': 'uint8',
            'int': 'uint256',          
            'uint': 'uint256',
            'address': 'uint160',
        }

    def parse(self, log_hex_str):
        if log_hex_str.startswith('0x'):
            log_hex_str = log_hex_str[2:]

        if len(log_hex_str) % self.pad_char_len != 0 :
            print ('error len of log_hex_str mod (pad_char_len) is not zero')

        splits = split_by_len(log_hex_str, 64)
        log_payload = []
        for prop in self.topic.properties:
            if prop.type == "address":
                splits, value = self._process_address(splits)
            elif prop.type in ("int", "uint", "uint32", "uint256", "uint8"):
                splits, value = self._process_int(splits, prop.type)
            else:
                print('Error, unsupported type {}'.format(prop.type))
                return None
            log_payload += [{'name': prop.name, 'type': prop.type, 'value':value}]

        return {'event': self.topic.event_name, 'payload': log_payload}

    def _process_address(self, splits):
        chars_to_read = int(self.type_mappings.get('address')[4:])//self.char_byte_size
        sp = splits.pop(0)
        address = '0x' + sp[-1*chars_to_read:]
        return splits, address

    def _process_int(self, splits, type):
        chars_to_read = int(self.type_mappings.get(type)[4:])//self.char_byte_size
        sp = splits.pop(0)
        value = int(sp[-1*chars_to_read:], 16)
        return splits, value

    # TODO add more types (string, ....)
