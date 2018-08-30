import unittest
import json
from eth_log.models.topic import Topic
from eth_log.models.topic_parser import TopicParser


class TestTopicParser(unittest.TestCase):
 
    def test_log_parsing_uint_address(self):
        """
        parsing a log hex string
        """
        json_str = """
            {
              "anonymous": false,
              "inputs": [
                {
                  "indexed": false,
                  "name": "owner",
                  "type": "address"
                },
                {
                  "indexed": false,
                  "name": "matronId",
                  "type": "uint256"
                },
                {
                  "indexed": false,
                  "name": "sireId",
                  "type": "uint256"
                },
                {
                  "indexed": false,
                  "name": "cooldownEndBlock",
                  "type": "uint256"
                }
              ],
              "name": "Pregnant",
              "type": "event"
            }
             """
        json_obj = json.loads(json_str)
        topic = Topic.from_json(json_obj)
        topic_parser = TopicParser(topic)
        test_log_hex_string = "000000000000000000000000de400f7e15c08b9d7a6746cf35e406e2e6f843cf00000000000000000000000000000000000000000000000000000000000e0bed00000000000000000000000000000000000000000000000000000000000a5a7000000000000000000000000000000000000000000000000000000000005f26ad"
        res = topic_parser.parse(test_log_hex_string)
        self.assertEqual(res.get('event'), 'Pregnant')
        self.assertEqual(res.get('payload')[0].get('name'), 'owner')
        self.assertEqual(res.get('payload')[0].get('type'), 'address')
        self.assertEqual(res.get('payload')[0].get('value'), '0xde400f7e15c08b9d7a6746cf35e406e2e6f843cf')
        self.assertEqual(res.get('payload')[3].get('name'), 'cooldownEndBlock')
        self.assertEqual(res.get('payload')[3].get('type'), 'uint256')
        self.assertEqual(res.get('payload')[3].get('value'), 6235821)

    def test_log_parsing_string_and_bytes(self):
        json_str = """
            {
              "anonymous": false,
              "inputs": [
                {
                  "indexed": false,
                  "name": "first",
                  "type": "uint"
                },
                {
                  "indexed": false,
                  "name": "second",
                  "type": "uint32[]"
                },
                {
                  "indexed": false,
                  "name": "third",
                  "type": "bytes10"
                },
                {
                  "indexed": false,
                  "name": "forth",
                  "type": "bytes"
                }
              ],
              "name": "f",
              "type": "event"
            }
             """
        json_obj = json.loads(json_str)
        topic = Topic.from_json(json_obj)
        topic_parser = TopicParser(topic)
        test_log_hex_string = "0x00000000000000000000000000000000000000000000000000000000000001230000000000000000000000000000000000000000000000000000000000000080313233343536373839300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e0000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000004560000000000000000000000000000000000000000000000000000000000000789000000000000000000000000000000000000000000000000000000000000000d48656c6c6f2c20776f726c642100000000000000000000000000000000000000"
        res = topic_parser.parse(test_log_hex_string)
        self.assertEqual(res.get('payload')[0].get('name'), 'first')
        self.assertEqual(res.get('payload')[0].get('type'), 'uint')
        self.assertEqual(res.get('payload')[0].get('value'), 291)
        self.assertEqual(res.get('payload')[1].get('name'), 'second')
        self.assertEqual(res.get('payload')[1].get('type'), 'uint32[]')
        self.assertEqual(res.get('payload')[1].get('value'), [1110, 1929])
        self.assertEqual(res.get('payload')[2].get('name'), 'third')
        self.assertEqual(res.get('payload')[2].get('type'), 'bytes10')
        self.assertEqual(res.get('payload')[2].get('value'), "1234567890")
        self.assertEqual(res.get('payload')[3].get('name'), 'forth')
        self.assertEqual(res.get('payload')[3].get('type'), 'bytes')
        self.assertEqual(res.get('payload')[3].get('value'), "Hello, world!")

