import re
from google.cloud import bigquery
from eth_log.models.eventlog import EventLog
from eth_log.models.topic_parser import TopicParser
from eth_log.models.function_call_parser import FunctionCallParser
from eth_log.models.function_call import FunctionCall


class GoogleBigqueryHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_id = 'bigquery-public-data'
        self.dataset_id = 'ethereum_blockchain'
        self.bigquery_client = bigquery.Client()

    def fetch_function_calls_by_signature(self, contract_address, function, 
                                 parsing=False,
                                 min_block_number=None, max_block_number=None, 
                                 min_block_timestamp=None, max_block_timestamp=None):
        query = """
            SELECT
                to_address,
                from_address,
                input,
                block_hash,
                block_number,
                nonce,
                gas,
                gas_price,
                receipt_gas_used,
                receipt_status,
                receipt_root,
                t.hash,
                transaction_index,
                block_timestamp
            FROM `{project_id}.{dataset_id}.transactions` as t
            WHERE to_address = '{to_address}' 
            AND STARTS_WITH(input, "{signature}") \n
        """.format(to_address=contract_address,
                   signature=function.signature,
                   project_id=self.project_id,
                   dataset_id=self.dataset_id)

        if min_block_number:
            query += 'AND block_number >= {} \n'.format(min_block_number)
        if max_block_number:
            query += 'AND block_number < {} \n'.format(max_block_number)
        if min_block_timestamp:
            query += 'AND block_timestamp >= "{}" \n'.format(min_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if max_block_timestamp:
            query += 'AND block_timestamp < "{}" \n'.format(max_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        query_job = self.bigquery_client.query(query)
        if self.verbose:
            print('sending query to bigquery:')
            query = re.sub(r'[\n]\W+|^\W+', '\n', query)
            print(query)
        results = query_job.result()  # Waits for job to complete.
        if not results:
            return []
        field_names = [f.name for f in results.schema]
        if parsing:
            function_call_parser = FunctionCallParser(function)
            return [function_call_parser.parse(FunctionCall.from_google_public_dataset_json(dict(zip(field_names, row)))) for row in results]
        else:
            return [FunctionCall.from_google_public_dataset_json(dict(zip(field_names, row))) for row in results] 


    def fetch_function_calls_and_events_by_function(self, contract_obj, function_obj,
                                                     list_of_other_contract_objs,
                                                     parsing=False,
                                                     min_block_number=None, max_block_number=None, 
                                                     min_block_timestamp=None, max_block_timestamp=None):

        query = """
            SELECT tx.*,
               log.data,
               log.log_index,
               log.topics,
               log.address as log_contract_address
            FROM `bigquery-public-data.ethereum_blockchain.transactions` as tx
            Left join `bigquery-public-data.ethereum_blockchain.logs` as log
            on log.block_number = tx.block_number 
               and log.transaction_hash = tx.hash 
               and log.transaction_index = tx.transaction_index
            WHERE tx.to_address = '{to_address}' 
            AND STARTS_WITH(tx.input, "{signature}") \n
        """.format(to_address=contract_obj.contract_address,
                   signature=function_obj.signature,
                   project_id=self.project_id,
                   dataset_id=self.dataset_id)

        if min_block_number:
            query += 'AND tx.block_number >= {} \n'.format(min_block_number)
        if max_block_number:
            query += 'AND tx.block_number < {} \n'.format(max_block_number)
        if min_block_timestamp:
            query += 'AND tx.block_timestamp >= "{}" \n'.format(min_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if max_block_timestamp:
            query += 'AND tx.block_timestamp < "{}" \n'.format(max_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        # order 
        query += 'order by log.block_number, log.transaction_index, log.log_index'
        query_job = self.bigquery_client.query(query)

        function_calls = {} # id 
        if self.verbose:
            print('sending query to bigquery:')
            query = re.sub(r'[\n]\W+|^\W+', '\n', query)
            print(query)
        results = query_job.result()  # Waits for job to complete.
        if not results:
            return []
        field_names = [f.name for f in results.schema]
        if parsing:
            function_call_parser = FunctionCallParser(function_obj)

        for row in results:
            data = dict(zip(field_names, row))
            id = str(data.get('block_number')) + '_' + data.get('hash')
            data['id'] = id
            if id not in function_calls:
                func = FunctionCall.from_google_public_dataset_json(data)
                if parsing:
                    func = function_call_parser.parse(func)
                function_calls[data.get('id')] = func

            func = function_calls.get(data.get('id'))
            if data.get('topics'):
                eventlog = EventLog.from_google_public_dataset_json(data)
                if parsing:
                    found = False
                    for topic in data.get('topics'):
                        if found:
                            break
                        for contract in [contract_obj] + list_of_other_contract_objs:
                            if found:
                                break
                            main_topic = contract.get_topic_by_fingerprint(topic)
                            if main_topic:
                                topic_parser = TopicParser(main_topic) 
                                eventlog = topic_parser.parse(eventlog)
                                found = True
                    if not found:
                        print('not found the right topic in contracts', data.get('topics'))
                func.eventlogs += [eventlog]
        return list(function_calls.values())

    def fetch_eventlogs_by_topic(self, contract_address, topic, 
                                 parsing=False,
                                 min_block_number=None, max_block_number=None, 
                                 min_block_timestamp=None, max_block_timestamp=None):
        query = """
            SELECT
                log_index,
                transaction_hash,  
                transaction_index,
                address,
                data,  
                topics,
                block_timestamp,  
                block_number,  
                block_hash
            FROM `{project_id}.{dataset_id}.logs` 
            WHERE address = '{address}' 
            AND '{topic}' in UNNEST(topics) \n
        """.format(address=contract_address,
                   topic=topic.fingerprint,
                   project_id=self.project_id,
                   dataset_id=self.dataset_id)

        if min_block_number:
            query += 'AND block_number >= {} \n'.format(min_block_number)
        if max_block_number:
            query += 'AND block_number < {} \n'.format(max_block_number)
        if min_block_timestamp:
            query += 'AND block_timestamp >= "{}" \n'.format(min_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        if max_block_timestamp:
            query += 'AND block_timestamp < "{}" \n'.format(max_block_timestamp.strftime("%Y-%m-%d %H:%M:%S"))

        query_job = self.bigquery_client.query(query)
        if self.verbose:
            print('sending query to bigquery:')
            query = re.sub(r'[\n]\W+|^\W+', '\n', query)
            print(query)
        results = query_job.result()  # Waits for job to complete.
        if not results:
            return []
        field_names = [f.name for f in results.schema]
        if parsing:
            topic_parser = TopicParser(topic)
            return [topic_parser.parse(EventLog.from_google_public_dataset_json(dict(zip(field_names, row)))) for row in results]
        else:
            return [EventLog.from_google_public_dataset_json(dict(zip(field_names, row))) for row in results] 
