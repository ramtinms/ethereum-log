import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from eth_log.models.eventlog import EventLog

INFURA_DEFAULT_HOST = 'https://api.infura.io/v1/jsonrpc'


class InfuraAPIHandler:

    def __init__(self, host=None, block_per_request=100, verbose=False):
        self._session = self._get_session()
        self._host = host
        if not host:
            self._host = INFURA_DEFAULT_HOST
        self.block_per_request = block_per_request
        self.verbose = verbose

    def _get_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """
            session with retry (supports backoff)
        """
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _send_request(self, endpoint, params):
        url = self._host + endpoint
        resp = self._session.get(url, params=params)
        if self.verbose:
            print('Calling {}'.format(resp.url))
        if resp.status_code == 200:
            return resp.json()
        else:
            print('Error calling api, status code {}: {}'.format(resp.status_code, resp.text))
            print('url:', url)
            print('params', params)
            return {'status': 'error'}

    def generate_block_ranges(self, min_block_number, max_block_number):
        if max_block_number - min_block_number <= self.block_per_request:
            return [(min_block_number,max_block_number)]
        else:
            ranges = []
            counter = min_block_number
            while counter < max_block_number:
                # Note from block is included
                ranges += [(counter , min(counter + self.block_per_request - 1, max_block_number))]
                counter += self.block_per_request
            return ranges

    def normalize_hex(self, input_str):
        if input_str[:2] != '0x':
            input_str = '0x'+ input_str
        return input_str

    def fetch_eventlogs_by_topic(self, contract_address, topic, min_block_number, max_block_number):
        endpoint = '/mainnet/eth_getLogs'
        address = self.normalize_hex(contract_address)
        for block_range in self.generate_block_ranges(min_block_number, max_block_number):
            topic = self.normalize_hex(topic.fingerprint)
            params_str = 'params=[{{"topics":["{topic}"], "address": "{address}", "fromBlock": "{from_block}", "toBlock": "{to_block}"}}]'.format(
                topic=topic,
                address=address,
                from_block=hex(block_range[0]),
                to_block=hex(block_range[1]))
            res = self._parse_response(self._send_request(endpoint, params_str))
            if res and len(res) > 0:
                # TODO fix this 
                if self.verbose:
                    print('{} eventlogs fetched for topic {} from block {} to block {}'.format(len(res), topic, block_range[0],block_range[1]))
            if res:
                return [EventLog.from_etherscan_json(log_json_obj) for log_json_obj in res]
        return None

    def _parse_response(self, response):
        if response.get("result"):
            return response.get('result')

