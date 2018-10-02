import re
from google.cloud import bigquery
from eth_log.models.eventlog import EventLog
from eth_log.models.topic_parser import TopicParser


class GoogleBigqueryHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_id = 'bigquery-public-data'
        self.dataset_id = 'ethereum_blockchain'
        self.bigquery_client = bigquery.Client()

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
