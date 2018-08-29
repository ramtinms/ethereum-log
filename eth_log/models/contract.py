import os
import json
import pandas as pd
from collections import defaultdict
from eth_log.models.topic import Topic
from eth_log.models.topic_parser import TopicParser

class Contract:

    def __init__(self, contract_address, contract_abi_str):
        self.topic_parsers = {}
        self.contract_address = contract_address
        abi_obj = json.loads(contract_abi_str)
        self.topics = []
        for item in abi_obj:
            if item.get('type') == "event":
                topic = Topic.from_json(item)
                topic_parser = TopicParser(topic)
                self.topics += [topic.fingerprint]
                self.topic_parsers[topic.fingerprint] = topic_parser
        self.eventlogs = defaultdict(list)
        self.total_eventlogs = 0

    def add_eventlog(self, eventlog_obj):
        # we parse by the first matched fingerprint
        for topic_fingerprint in eventlog_obj.topic_fingerprints:
            if topic_fingerprint in self.topic_parsers:
                res = self.topic_parsers[topic_fingerprint].parse(eventlog_obj.log_hex_str_data)
                eventlog_obj.event_name = res['event']
                eventlog_obj.data = res['payload']
                self.eventlogs[res['event']] += [eventlog_obj]
                self.total_eventlogs += 1
                if self.total_eventlogs % 1000 == 0:
                    print('{}k eventlogs added to contract {}'.format(self.total_eventlogs//1000, self.contract_address))
                return

    def export_eventlogs_to_csv_files(self, output_directory_path):
        if not os.path.exists(output_directory_path):
                os.makedirs(output_directory_path)
        for event_name, eventlogs in self.eventlogs.items():
            df = pd.DataFrame([eventlog.get_dataframe() for eventlog in eventlogs])
            file_name = event_name + '_events.csv'
            df.to_csv(os.path.join(output_directory_path, file_name))
