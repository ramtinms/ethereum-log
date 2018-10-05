import json
from eth_log.models.topic import Topic
from eth_log.models.function import Function


class Contract:

    def __init__(self, contract_address, contract_abi_str):
        self.contract_address = contract_address
        self.contract_abi_str = contract_abi_str
        self.topics_by_event_name = {}
        self.topics_by_fingerprint = {}
        self.functions_by_name = {}
        abi_obj = json.loads(contract_abi_str)
        # self.topics = []
        for item in abi_obj:
            if item.get('type') == "event":
                topic = Topic.from_json(item)
                self.topics_by_event_name[topic.name] = topic
                self.topics_by_fingerprint[topic.fingerprint] = topic
                # self.topics += [topic]
            elif item.get('type') == "function":
                function = Function.from_json(item)
                self.functions_by_name[function.name] = function

    def get_topics(self):
        return self.topics_by_event_name.values() 

    def get_topic_by_event_name(self, name):
        return self.topics_by_event_name.get(name)

    def get_topic_by_fingerprint(self, fingerprint):
        return self.topics_by_fingerprint.get(fingerprint)

    def get_functions(self):
        return self.functions_by_name.values() 

    def get_functions_by_name(self, name):
        return self.functions_by_name.get(name)
