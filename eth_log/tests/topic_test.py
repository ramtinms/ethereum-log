import unittest
import json
from eth_log.models.topic import Topic


class TestTopic(unittest.TestCase):
 
    def test_from_json(self):
        """
        Creating a topic object from json
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
        self.assertEqual(topic.event_name, 'Pregnant')
        self.assertEqual(topic.properties[0].name, 'owner')
        self.assertEqual(topic.properties[0].type, 'address')
        self.assertEqual(topic.properties[3].name, 'cooldownEndBlock')
        self.assertEqual(topic.properties[3].type, 'uint256')
        ideal_fingerprint = '0x241ea03ca20251805084d27d4440371c34a0b85ff108f6bb5611248f73818b80'
        self.assertEqual(topic.fingerprint, ideal_fingerprint)
