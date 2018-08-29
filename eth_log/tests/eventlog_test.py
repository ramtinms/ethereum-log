import unittest
import json
from eth_log.models.eventlog import EventLog


class TestEventLog(unittest.TestCase):
 
    def test_from_etherscan_json(self):
        test_log_json_str = """
        {  "address": "0x06012c8cf97bead5deae237070f9587f8e7a266d",
          "topics": [
            "0x241ea03ca20251805084d27d4440371c34a0b85ff108f6bb5611248f73818b80"
          ],
          "data": "0x00000000000000000000000016205a6048b6af17f1ac1a009bbf2ed9289e692100000000000000000000000000000000000000000000000000000000000df37700000000000000000000000000000000000000000000000000000000000de76100000000000000000000000000000000000000000000000000000000005f3bf7",
          "blockNumber": "0x5f2577",
          "logIndex": "0x74",
          "gasPrice": "0xb368f480",
          "gasUsed": "0x13871",
          "timeStamp": "0x5b86c260",
          "transactionHash": "0xc2146292fc3876145fc75af47a382ed23e94d8f9e8e6b7a3aca16ac6ee5373c8",
          "transactionIndex": "0x56"
        }
        """
        eventlog_obj = EventLog.from_etherscan_json(json.loads(test_log_json_str))
        self.assertEqual(eventlog_obj.block_number, 6235511)
        self.assertEqual(eventlog_obj.log_index, 116)
        self.assertEqual(eventlog_obj.topic_fingerprints, ['0x241ea03ca20251805084d27d4440371c34a0b85ff108f6bb5611248f73818b80'])
        self.assertEqual(eventlog_obj.log_hex_str_data, '0x00000000000000000000000016205a6048b6af17f1ac1a009bbf2ed9289e692100000000000000000000000000000000000000000000000000000000000df37700000000000000000000000000000000000000000000000000000000000de76100000000000000000000000000000000000000000000000000000000005f3bf7')
        self.assertEqual(eventlog_obj.gas_price, 3010000000)
        self.assertEqual(eventlog_obj.gas_used, 79985)
        self.assertEqual(eventlog_obj.tx_hash, '0xc2146292fc3876145fc75af47a382ed23e94d8f9e8e6b7a3aca16ac6ee5373c8')
        self.assertEqual(eventlog_obj.tx_index, 86)
        self.assertEqual(eventlog_obj.timestamp.year, 2018)
        self.assertEqual(eventlog_obj.timestamp.month, 8)
        self.assertEqual(eventlog_obj.timestamp.day, 29)
        self.assertEqual(eventlog_obj.timestamp.hour, 15)
        self.assertEqual(eventlog_obj.timestamp.minute, 57)
        self.assertEqual(eventlog_obj.timestamp.second, 20)
