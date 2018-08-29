import unittest
import json
from eth_log.models.topic import Topic
from eth_log.models.topic_parser import TopicParser


class TestTopicParser(unittest.TestCase):
 
    def test_log_parsing(self):
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
