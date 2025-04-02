from atlassian import Confluence
import json, toml
import dotenv
import os
import logging
from agent_utils.schemas.models import ConfluenceBQMapping, ConfluenceBQPage

class ConfluenceConnector(): 
    '''
    This class interfaces with the Confluence API to:
    - Initialize the Confluence connection
    - Retrieve pages with specified labels
    - Provide a consistent interface for retrieving confluence page content
    - Retrieve html content for each page
    '''
    def __init__(self, config=None):
        dotenv.load_dotenv()
        self.config = config
        self.create_connection()

    def create_connection(self):
        confluence = Confluence(
            url=self.config['confluence']['connector']['base_url'], #Base URL for Confluence instance
            username=os.getenv('CONFLUENCE_API_EMAIL'), #TODO - move all auth to secrets manager
            password=os.getenv('CONFLUENCE_API_KEY')
        )
        
        if not confluence:
            raise Exception("Confluence API failed to initialize.")
        else:
            logging.info("Confluence API initialized.")
        self.connection = confluence

    def get_pages_by_label(self, label):
        pages = self.connection.get_all_pages_by_label(label, expand='version,ancestors')
        return pages
    
    def get_page_by_id(self, page_id, doc_format='body.storage'): 
        return self.connection.get_page_by_id(page_id, expand=doc_format)

    def get_page_data(self, page_id):
        page = self.get_page_by_id(page_id)
        return page

    # gcp-wow-food-fco-auto-dev

    def get_gcp_mapping(self, **kwargs):
        """
        Returns a mapping of confluence pages to GCP table and dataset names.
        {confluence_page_id: ConfluenceBQPage}
        """
        dataset_label = self.config['confluence']['connector']['dataset_label']
        table_label = self.config['confluence']['connector']['table_label']

        if (dataset_label is None) or (table_label is None):
            logging.error("Failed to retrieve dataset or table labels from [config.confluence.connector].")
            return None

        dataset_pages = self.get_pages_by_label(dataset_label)
        table_pages = self.get_pages_by_label(table_label)
        gcp_mapping = {page['title'].split(" ")[0].lower():page['id'] for page in dataset_pages + table_pages}
        gcp_mapping = {k: v for k, v in gcp_mapping.items() if k.split('.')[0] in self.config['bigquery']['valid_datasets']}
        return gcp_mapping
    
    def get_bigquery_documentation_context(self, bq_resources=None):
        """
        Gets the confluence page content for all GCP Tables.
        page_ids = [confluence_page_id]
        """
        mapping = self.get_gcp_mapping()
        # Filter config.valid_datasets
        mapping = {k: v for k, v in mapping.items() if k in self.config['bigquery']['valid_datasets']}
        if bq_resources is not None:
            mapping = {k: v for k, v in mapping.items() if k in bq_resources}  

        page_ids = [v for k, v in mapping.items()]
        for page_id in page_ids:
            page = self.get_page_by_id(page_id)
            page_content = page['body']['storage']['value']
            page_title = page['title']
        ###############################################

    def get_pages_from_qualified_names(self, qualified_names: list[str], **kwargs): #eg. ['product.sales']
        page_ids = self.get_page_ids_from_qualified_names(qualified_names, **kwargs)
        return self.get_bigquery_documentation_context(page_ids, **kwargs)

    def get_page_ids_from_qualified_names(self, qualified_names: list[str], **kwargs):
        gcp_mapping = kwargs.get('gcp_mapping', self.get_gcp_mapping())
        page_ids = [k for k, v in gcp_mapping.items() if f"{v['dataset_name']}.{v['table_name']}" in qualified_names]
        return page_ids


from gcs_connector import GoogleCloudStorageConnector
gcs_connector = GoogleCloudStorageConnector()
config = gcs_connector.load_toml()

conf_conn = ConfluenceConnector(config)
conf_conn.get_gcp_mapping()
"test"
