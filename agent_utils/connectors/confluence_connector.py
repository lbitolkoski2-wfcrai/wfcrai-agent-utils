from atlassian import Confluence
import json, toml
import dotenv
import os
import logging
from agent_utils.schemas.models import ConfluenceBQPage
from agent_utils.components.confluence_parser import ConfluenceParser

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
        self.bq_mapping = self.get_bq_mapping()

    def create_connection(self):
        confluence = Confluence(
            url=self.config['confluence']['connector']['base_url'],
            username=os.getenv('CONFLUENCE_API_EMAIL'),
            password=os.getenv('CONFLUENCE_API_KEY')
        )
        
        if not confluence:
            raise Exception("Confluence API failed to initialize.")
        else:
            logging.info("Confluence API initialized.")
        self.connection = confluence

    def get_pages_by_label(self, label):
        pages = self.connection.get_all_pages_by_label(label, expand='version,ancestors', limit=1000)
        return pages
    
    # Returns the confluence page content for a given page ID
    def get_page_by_id(self, page_id: str, doc_format='body.storage') -> ConfluenceBQPage:
        page = self.connection.get_page_by_id(page_id, expand=doc_format)
        qualified_name = page['title'].split(" ")[0].lower() # page title is the resource name
        resource_type = "dataset" if "." not in page['title'] else "table" # if the page title contains a dot, it is a table
        dataset_name = qualified_name.split(".")[0]
        table_name = qualified_name.split(".")[1] if resource_type == "table" else None
        #Strip unneccessary HTML content from the page
        page_content = ConfluenceParser.clean_html(page['body']['storage']['value'])
        return ConfluenceBQPage(
            bq_resource_type=resource_type,
            bq_table_name= table_name,
            bq_dataset_name= dataset_name,
            bq_qualified_name= qualified_name,
            confluence_page_content= page_content,
            confluence_page_id=page_id,
        )

    def get_cql(self, cql_string):
        results = (self.connection.cql(cql, limit=1000))
        results_mapping = {}
        for result in results:
            space = result['resultGlobalContainer']['title']
            title = result['content']['title']
            page_id = result['content']['id']
        results = self.connection.cql(cql_string)

    # gcp-wow-food-fco-auto-dev

    def synchronize_confluence(self):
        """
        Synchronizes certain pages from WFCR space to the WFCRAI space.
        """
        pages_to_sync = os.getenv('PAGES_TO_SYNC', "opal,sphere,bamboo_rose,plexus").split(",")
        title_queries = [f'title ~ "{page}*"' for page in pages_to_sync]
        from_cql = "type=page AND (" + " OR ".join(title_queries) + ") AND space = WFCR"
        to_cql = "type=page AND (" + " OR ".join(title_queries) + ") AND space = WFCRAI"
        
        from_results = self.connection.cql(from_cql, limit=1000)
        to_results = self.connection.cql(to_cql, limit=1000)
        
        from_results_dict = {result['content']['title']: result for result in from_results['results']}
        to_results_dict = {result['content']['title']: result for result in to_results['results']}
        
        results_mapping = {}
        for title, from_result in from_results_dict.items():
            to_result = to_results_dict.get(title)
            results_mapping[title] = {
                'from': from_result,
                'to': to_result
            }

        for title, result in results_mapping.items():
            if result['to'] is None:
                pass
                # Create a new page in WFCRAI space
                self.connection.create_page(
                    space='WFCRAI',
                    title=title,
                    body=self.connection.get_page_by_id(result['from']['content']['id'])['body']['storage']['value'],
                    parent_id=result['from']['content']['ancestors'][0]['id'],
                    representation='storage'
                )
            else:
                # Update the existing page in WFCRAI space
                page_content = self.connection.get_page_by_id(result['from']['content']['id'], expand='body.storage')
                print(f"from: {result['from']['title']} to: {result['to']['title']}")
                self.connection.update_page(
                    page_id=result['to']['content']['id'],
                    title=title,
                    body=page_content['body']['storage']['value'],
                    representation='storage'
                )

    def get_bq_mapping(self, **kwargs):
        """
        Returns a mapping of confluence pages to BQ table and dataset names.
        {confluence_page_id: bq_resource_name}
        """
        dataset_label = self.config['confluence']['connector']['dataset_label']
        table_label = self.config['confluence']['connector']['table_label']

        if (dataset_label is None) or (table_label is None):
            logging.error("Failed to retrieve dataset or table labels from [config.confluence.connector].")
            return None

        dataset_pages = self.get_pages_by_label(dataset_label)
        table_pages = self.get_pages_by_label(table_label)
        bq_mapping = {page['title'].split(" ")[0].lower():page['id'] for page in dataset_pages + table_pages}
        bq_mapping = {k: v for k, v in bq_mapping.items() if k.split('.')[0] in self.config['bigquery']['valid_datasets']}
        return bq_mapping
    
    def get_bigquery_documentation_context(self, bq_resources=None):
        """
        Gets the confluence page content for all BQ Tables.
        bq_resources: list of bq resources [dataset.table] to include. if None, all resources are included.
        """
        #Filter out only requested and valid resources
        mapping = self.get_bq_mapping()
        mapping = {k: v for k, v in mapping.items() if k.split('.')[0] in self.config['bigquery']['valid_datasets']}
        if bq_resources is not None:
            mapping = {k: v for k, v in mapping.items() if k in bq_resources}  

        # Get context for each page
        page_ids = mapping.values()
        pages = [self.get_page_by_id(page_id) for page_id in page_ids]
        bq_documentation = {page.bq_qualified_name: page.model_dump() for page in pages}
        return bq_documentation

