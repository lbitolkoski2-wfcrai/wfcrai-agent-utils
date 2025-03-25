import google.cloud.storage as storage
import toml

class GoogleCloudStorageConnector():
    """
    Google Cloud Storage connector class.
    Initializes a connection to Google Cloud Storage.
    Provides helper functions to interact with Google Cloud Storage.
    """
    def __init__(self, bucket_name="wfcrai-agents"):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def load_toml(self, gs_url="data-agent/config/bundled.toml"):
        blob = self.bucket.blob(gs_url)
        content = blob.download_as_text()
        return toml.loads(content)