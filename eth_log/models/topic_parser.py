import re
from eth_log.utils import split_by_len
from eth_log.utils import validate_address

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
            'bytes': 'bytes',
            'string': 'bytes',
            'uint32[]': 'uint32[]',
            'uint8[]': 'uint8[]',
            'uint256[]': 'uint256[]',
            'bytes10': 'bytes10'
        }

    def parse(self, eventlog_obj):
        log_hex_str = eventlog_obj.log_hex_str_data

        if log_hex_str.startswith('0x'):
            log_hex_str = log_hex_str[2:]

        if len(log_hex_str) % self.pad_char_len != 0 :
            print ('error len of log_hex_str mod (pad_char_len) is not zero')

        splits = split_by_len(log_hex_str, 64)
        log_payload = []
        processed_splits = 0
        other_topics = eventlog_obj.topic_fingerprints[1:].copy()
        for prop in self.topic.properties:
            if prop.indexed:
                indexed_value = other_topics.pop() 
                if prop.type == "address":
                    _ , value = self._process_address([indexed_value])
                elif prop.type in ("int", "uint", "uint32", "uint256", "uint8"):
                    _ , value = self._process_int([indexed_value], prop.type)
                else:
                    print('Error, unsupported type {}'.format(prop.type))
                    return None
            else:
                if prop.type == "address":
                    splits, value = self._process_address(splits)
                    processed_splits+=1
                elif prop.type in ("int", "uint", "uint32", "uint256", "uint8"):
                    splits, value = self._process_int(splits, prop.type)
                    processed_splits+=1
                elif prop.type in ("bytes", "string"):
                    splits, value, n = self._process_string(splits, prop.type, processed_splits)
                    processed_splits+=n
                elif prop.type in ("uint8[]", "uint32[]", "uint256[]"):
                    splits, value, n = self._process_array(splits, prop.type, processed_splits)
                    processed_splits+=n
                elif re.match(r"bytes[0-9]+", prop.type):
                    splits, value = self._process_bytes(splits, prop.type)
                    processed_splits+=1
                else:
                    print('Error, unsupported type {}'.format(prop.type))
                    return None
            log_payload += [{'name': prop.name, 'type': prop.type, 'value':value}]

            eventlog_obj.data = log_payload
            eventlog_obj.event_name = self.topic.name
        return eventlog_obj

    def _process_address(self, splits):
        chars_to_read = int(self.type_mappings.get('address')[4:])//self.char_byte_size
        sp = splits.pop(0)
        address = sp[-1*chars_to_read:]
        address = validate_address(address)
        return splits, address

    def _process_int(self, splits, type):
        chars_to_read = int(self.type_mappings.get(type)[4:])//self.char_byte_size
        sp = splits.pop(0)
        value = int(sp[-1*chars_to_read:], 16)
        return splits, value

    def _process_string(self, splits, type, processed_splits):
        # index to read content
        n = 0
        sp = splits.pop(0)
        n += 1
        if sp.startswith('0x'):
            sp = sp[2:]
        split_index_to_read_content = int(sp, 16) * 2 // self.pad_char_len - processed_splits - 1
        sp = splits.pop(split_index_to_read_content)
        n += 1
        bytes_to_read = int(sp, 16)
        chars_to_read = bytes_to_read * 2
        # how many to read
        hex_content = ''
        # more to read
        while len(hex_content) - chars_to_read < 0:
            sp = splits.pop(split_index_to_read_content)
            hex_content = hex_content + sp
            n += 1

        value = bytes.fromhex(hex_content[:chars_to_read]).decode('utf-8')
        return splits, value, n

    def _process_array(self, splits, type, processed_splits):
        n = 0
        chars_to_read = int(self.type_mappings.get(type)[4:-2])//self.char_byte_size
        # index to read content
        sp = splits.pop(0)
        n += 1
        if sp.startswith('0x'):
            sp = sp[2:]
        split_index_to_read_content = int(sp, 16) * 2 //self.pad_char_len - processed_splits - 1
        sp = splits.pop(split_index_to_read_content)
        n += 1
        splits_to_read = int(sp, 16)
        # how many to read
        array = []
        for _ in range(splits_to_read):
            sp = splits.pop(split_index_to_read_content)
            array += [int(sp[-1*chars_to_read:], 16)]
            n += 1
        return splits, array, n

    def _process_bytes(self, splits, type):
        bytes_to_read = int(type.replace('bytes',''))
        chars_to_read = bytes_to_read*2
        sp = splits.pop(0)
        # TODO for bytes bigger than 32 bytes ?
        if sp.startswith('0x'):
            sp = sp[2:]
        value = bytes.fromhex(sp[:chars_to_read]).decode('utf-8')
        return splits, value

    # TODO add more types (fixed, ...)
