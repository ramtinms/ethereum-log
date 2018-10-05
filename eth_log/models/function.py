import sha3
from collections import namedtuple

FunctionInput = namedtuple('FunctionInput', ['name', 'type'])
FunctionOutput = namedtuple('FunctionOutput', ['name', 'type'])

class Function:
    def __init__(self, function_name, list_of_inputs, list_of_outputs, payable, state_mutability):
        self.name = function_name
        self.payable = payable
        self.state_mutability = state_mutability

        self.inputs = list_of_inputs
        self.outputs = list_of_outputs
        # TODO FROM HERE
        self.description = function_name + '(' + ', '.join([inp.name + ' ('+inp.type + ')' for inp in list_of_inputs]) + ')'
        self.signature = self._build_signature(function_name, list_of_inputs)

    def _build_signature(self, function_name, list_of_inputs):
        input_string = function_name + '(' + ','.join([inp.type for inp in list_of_inputs]) + ')'
        input_string = input_string.replace(' ', '')
        hashfunc = sha3.keccak_256()
        hashfunc.update(bytes(input_string, 'utf-8'))
        return '0x' + hashfunc.hexdigest()[:8]

    def check_signature(self, signature):
        return signature == self.signature

    @classmethod
    def from_json(cls, json_obj):
        if json_obj.get('type') != 'function':
            print('wrong type of json_obj, type is not function!')
            return None
        name = json_obj.get('name')
        payable = json_obj.get('payable')
        state_mutability = json_obj.get('stateMutability')
        inputs = []
        outputs = []
        for inp in json_obj.get('inputs', []):
            inputs += [FunctionInput(inp.get('name'), inp.get('type'))]
        for outp in json_obj.get('outputs', []):
        	outputs += [FunctionOutput(outp.get('name'), outp.get('type'))]
        return cls(name, inputs, outputs, payable, state_mutability)

