import unittest
import json
from eth_log.models.function import Function


class TestTopic(unittest.TestCase):
 
    def test_from_json(self):
        """
        Creating a topic object from json
        """
        json_str = """
            {
                "constant": true,
                "inputs": [
                  {
                    "name": "_matronId",
                    "type": "uint256"
                  },
                  {
                    "name": "_sireId",
                    "type": "uint256"
                  }
                ],
                "name": "canBreedWith",
                "outputs": [
                  {
                    "name": "",
                    "type": "bool"
                  }
                ],
                "payable": false,
                "stateMutability": "view",
                "type": "function"
              }
             """
        json_obj = json.loads(json_str)
        function = Function.from_json(json_obj)
        self.assertEqual(function.name, 'canBreedWith')
        self.assertEqual(function.inputs[0].name, '_matronId')
        self.assertEqual(function.inputs[0].type, 'uint256')
        self.assertEqual(function.outputs[0].name, '')
        self.assertEqual(function.outputs[0].type, 'bool')
        ideal_signature = '0x46d22c70'
        self.assertEqual(function.signature, ideal_signature)
