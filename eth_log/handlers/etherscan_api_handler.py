import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.parse
from eth_log.models.eventlog import EventLog

DEFAULT_HOST = 'https://api.etherscan.io'


class EtherscanAPIHandler:

    def __init__(self, api_key, host=None, block_per_request=50, verbose=False):
        self._session = self._get_session()
        self._host = host
        if not host:
            self._host = DEFAULT_HOST
        self._api_key = api_key
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
        url = urllib.parse.urljoin(self._host, endpoint)
        params['apikey'] = self._api_key
        resp = self._session.get(url, params=params)
        if self.verbose:
            print('Calling {}'.format(resp.url))
        if resp.status_code == 200:
            return resp.json()
        else:
            print('error calling api, status code {}: {}'.format(resp.status_code, resp.text))
            return {'status': 'error'}

    def fetch_contract_abi_string(self, contract_address):
        endpoint = '/api'
        params = {
            'module': 'contract',
            'action': 'getabi',
            'address': contract_address,
            'apikey': self._api_key
        }
        res = self._parse_response(self._send_request(endpoint, params))
        return res

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
                
    def fetch_eventlogs_by_contract(self, contract_obj, min_block_number, max_block_number):
        endpoint = '/api'
        params = {
            'module': 'logs',
            'action': 'getLogs',
            'address': contract_obj.contract_address,
            'apikey': self._api_key
        }

        for block_range in self.generate_block_ranges(min_block_number, max_block_number):
            params['fromBlock'] = block_range[0]
            params['toBlock'] = block_range[1]
            for topic in contract_obj.topics:
                params['topic0'] = topic
                res = self._parse_response(self._send_request(endpoint, params))
                if res and len(res) > 0:
                    if self.verbose:
                        print('{} eventlogs fetched for topic {} from block {} to block {}'.format(len(res), topic, block_range[0],block_range[1]))
                    if len(res) == 1000:
                        print('warning, you have exactly 1000 results in this request, you might have try to use smaller block_per_request.')
                    for log_json_obj in res:
                        contract_obj.add_eventlog(EventLog.from_etherscan_json(log_json_obj))

    def _parse_response(self, response):
        if response.get("status", '') == "1" and response.get("message", '') == "OK":
            if response.get('result'):
                return response.get('result')

