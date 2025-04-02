from agent_utils.connectors import GoogleCloudStorageConnector, ConfluenceConnector, LLMConnector
gcs_connector = GoogleCloudStorageConnector()
config = gcs_connector.load_toml()
confluence_connector = ConfluenceConnector(config)

result = confluence_connector.get_gcp_mapping() 
import json
with open("tests/confluence_context.json", "w") as f:
    f.write(json.dumps(result))

