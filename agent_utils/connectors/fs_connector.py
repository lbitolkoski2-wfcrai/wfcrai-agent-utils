import logging
from google.cloud import firestore

class FirestoreConnector():
    """
    Firestore connector class.
    Initializes a connection to Google Cloud Firestore.
    Provides helper functions to interact with Firestore.
    """
    def __init__(self):
        self.client = firestore.Client()

    def get_document(self, collection_name, document_id):
        try:
            doc_ref = self.client.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                logging.info(f"Document {document_id} does not exist in collection {collection_name}.")
                return None
        except Exception as e:
            logging.error(f"Error fetching document: {e}")
            return None

    def update_document(self, collection_name, document_id, data):
        try:
            doc_ref = self.client.collection(collection_name).document(document_id)
            doc_ref.update(data)
            logging.info(f"Document {document_id} updated successfully in collection {collection_name}.")
        except Exception as e:
            logging.error(f"Error updating document: {e}")

    def create_document(self, collection_name, document_id, data):
        try:
            doc_ref = self.client.collection(collection_name).document(document_id)
            doc_ref.set(data)
            logging.info(f"Document {document_id} created successfully in collection {collection_name}.")
        except Exception as e:
            logging.error(f"Error creating document: {e}")

    def delete_document(self, collection_name, document_id):
        """
        Deletes a document from a Firestore collection.
        """
        try:
            doc_ref = self.client.collection(collection_name).document(document_id)
            doc_ref.delete()
            logging.info(f"Document {document_id} deleted successfully from collection {collection_name}.")
        except Exception as e:
            logging.error(f"Error deleting document: {e}")