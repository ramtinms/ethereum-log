import re
from eth_log.utils import split_by_len
from eth_log.utils import validate_address

class FunctionCallParser:

    def __init__(self, function):
        self.function = function
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

    def parse(self, transaction_obj):
        data_hex_str = transaction_obj.data
        assert self.function.signature == data_hex_str[:10]
        
        data_hex_str = data_hex_str[10:]

        if len(data_hex_str) % self.pad_char_len != 0 :
            raise ValueError('error len of data_hex_str mod (pad_char_len) is not zero')

        splits = split_by_len(data_hex_str, 64)
        input_data = []
        processed_splits = 0
        for inp in self.function.inputs:
            if inp.type == "address":
                splits, value = self._process_address(splits)
                processed_splits+=1
            elif inp.type in ("int", "uint", "uint32", "uint256", "uint8"):
                splits, value = self._process_int(splits, inp.type)
                processed_splits+=1
            elif inp.type in ("bytes", "string"):
                splits, value, n = self._process_string(splits, inp.type, processed_splits)
                processed_splits+=n
            elif inp.type in ("uint8[]", "uint32[]", "uint256[]"):
                splits, value, n = self._process_array(splits, inp.type, processed_splits)
                processed_splits+=n
            elif re.match(r"bytes[0-9]+", inp.type):
                splits, value = self._process_bytes(splits, inp.type)
                processed_splits+=1
            else:
                print('Error, unsupported type {}'.format(inp.type))
                return None
            input_data += [{'name': inp.name, 'type': inp.type, 'value':value}]
            transaction_obj.input_data = input_data
            transaction_obj.function_name = self.function.name
        return transaction_obj

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
