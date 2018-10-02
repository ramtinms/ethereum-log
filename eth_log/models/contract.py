import json
from eth_log.models.topic import Topic


class Contract:

    def __init__(self, contract_address, contract_abi_str):
        self.contract_address = contract_address
        self.contract_abi_str = contract_abi_str
        self.topics_by_event_name = {}
        abi_obj = json.loads(contract_abi_str)
        # self.topics = []
        for item in abi_obj:
            if item.get('type') == "event":
                topic = Topic.from_json(item)
                self.topics_by_event_name[topic.name] = topic
                # self.topics += [topic]

    def get_topics(self):
        return self.topics_by_event_name.values() 

    def get_topic_by_event_name(self, name):
        return self.topics_by_event_name.get(name)
