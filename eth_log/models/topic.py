import sha3
from collections import namedtuple

TopicProperty = namedtuple('TopicProperty', ['name', 'type'])

class Topic:
    def __init__(self, event_name, ordered_topic_properties):
        self.event_name = event_name
        self.properties = ordered_topic_properties
        self.fingerprint = self._build_finger_print(event_name, ordered_topic_properties)

    def _build_finger_print(self, event_name, ordered_topic_properties):
        input_string = event_name + '(' + ','.join([prop.type for prop in ordered_topic_properties]) + ')'
        # replace unwanted spaces just in case
        input_string = input_string.replace(' ', '')
        hashfunc = sha3.keccak_256()
        hashfunc.update(bytes(input_string, 'utf-8'))
        # TODO cutting based on size
        return '0x' + hashfunc.hexdigest()

    def check_finger_print(self, fingerprint):
        return fingerprint == self.fingerprint

    @classmethod
    def from_json(cls, json_obj):
        if json_obj.get('type') != 'event':
            print('wrong type of json_obj, type is not event!')
            return None
        name = json_obj.get('name')
        properties = []
        for inp in json_obj.get('inputs', []):
            properties += [TopicProperty(inp.get('name'), inp.get('type'))]
        return cls(name, properties)
