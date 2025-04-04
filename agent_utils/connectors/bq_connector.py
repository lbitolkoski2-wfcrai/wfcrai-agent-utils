import os
import dotenv
from google.cloud import bigquery
import json
import logging
from google.cloud.bigquery.job import QueryJobConfig

class BigQueryConnector():
    def __init__(self, config=None):
        self.config = config
        dotenv.load_dotenv()
        self.client = bigquery.Client(
            project=config['bigquery']['project_id']
        )


        self.valid_datasets = config['bigquery']['valid_datasets']
        self.project_id = config['bigquery']['project_id']
        self.gcp_region = config['bigquery']['region']
        logging.info(f"BigQueryConnector: initialized with project_id: {self.project_id} and region: {self.gcp_region}")
        logging.info(f"BigQueryConnector: Valid datasets: {self.valid_datasets}")
        pass

    def project_tables(self):
        schema_query = f"""
        SELECT CONCAT(table_schema,'.', table_name) as qualified_name, table_schema as dataset_name, table_name, option_value as description
        FROM `{self.project_id}.{self.gcp_region}.INFORMATION_SCHEMA.TABLE_OPTIONS`  
        WHERE option_name="description"
        AND table_schema in UNNEST({self.valid_datasets})
        """
        schema_query = schema_query.replace('\n', '').replace('\r', '')
        rows = self.execute_query(schema_query)
        results = [dict(row) for row in rows]
        return results

    def project_columns(self):
        schema_query = f"""
            SELECT CONCAT(table_schema,'.', table_name) as qualified_name, table_schema as dataset_name, table_name, column_name, data_type
            FROM `{self.project_id}.{self.gcp_region}.INFORMATION_SCHEMA.COLUMNS` 
            WHERE table_schema in UNNEST({self.valid_datasets})"""
        schema_query = schema_query.replace('\n', '').replace('\r', '')
        rows = self.execute_query(schema_query)
        results = [dict(row) for row in rows]
        return results
    
    def execute_query(self, query, **kwargs):
        job_config = QueryJobConfig(**kwargs)
        query_result = self.client.query_and_wait(query, job_config=job_config)
        return query_result
    
    async def async_execute_query(self, query, **kwargs):
        job_config = QueryJobConfig(**kwargs)
        try:
            job = self.client.query(query, job_config=job_config)
            return {"result": job, "error": None}
        except Exception as e:
            logging.error(f"query execution failed: {e}")
            return {"result": None, "error": str(e)}

    async def run_stored_procedure(self, procedure_name, **kwargs):
        job_config = QueryJobConfig(**kwargs)

        query = f"CALL {procedure_name}();"
        try:
            job = self.client.query(query, job_config=job_config)
            return {"result": job, "error": None}
        except Exception as e:
            logging.error(f"query execution failed: {e}")
            return {"result": None, "error": str(e)}
        

    def validate_query(self, query):
        # Use dry run to validate the query
        bq_job = {"job_id": None, "result": None, "error": None}
        q_config = QueryJobConfig(dry_run=True)
        try:
            result = self.client.query(query, job_config=q_config)
        except Exception as e:
            logging.error(f"Query validation failed: {e}")
            return {"job_id": None, "valid": False, "message": str(e)}
        return {"valid": True, "message": "Query is valid"}

