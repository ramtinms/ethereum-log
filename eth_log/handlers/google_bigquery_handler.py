import json
from google.cloud import bigquery
from eth_log.models.eventlog import EventLog


class GoogleBigqueryHandler:

    def __init__(self, verbose=False):
        self.verbose = verbose
        self.project_id = 'bigquery-public-data'
        self.dataset_id = 'ethereum_blockchain'
        self.bigquery_client = bigquery.Client()
        # self.dataset = bigquery.Dataset(self.bigquery_client.dataset(self.dataset_id))

    def fetch_event_logs(self, contract_obj, min_block_number, max_block_number):
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
                join `{project_id}.{dataset_id}.logs`

            WHERE address = '{address}'
            AND block_number >= {min_block_number}
            AND block_number < {max_block_number}
        """.format(address=contract_obj.contract_address,
                   project_id=self.project_id,
                   dataset_id=self.dataset_id,
                   min_block_number=min_block_number,
                   max_block_number=max_block_number)

        query_job = self.bigquery_client.query(query)
        if self.verbose:
            print('sending query to bigquery:')
            print(query)
        results = query_job.result()  # Waits for job to complete.
        field_names = [f.name for f in query_job.schema]
        for row in results:
            contract_obj.add_eventlog(EventLog.from_google_public_dataset_json(zip(field_names, row)))

    # def fetch_eventlogs_by_contract_from_file(self, json_dump_file, contract_obj, min_block_number, max_block_number):
    #     with open(json_dump_file) as inp:
    #         for line in inp:
    #             if line:
    #                 data = json.loads(line)
    #                 # TODO add constraints over block numbers
    #                 # has intersection
    #                 if data['address'] == contract_obj.contract_address and not set(contract_obj.topics).isdisjoint(data['topics']):
    #                     contract_obj.add_eventlog(EventLog.from_google_public_dataset_json(data))