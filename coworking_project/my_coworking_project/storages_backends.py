# my_coworking_project/storages_backends.py
from storages.backends.azure_storage import AzureStorage
import os

class AzureMediaStorage(AzureStorage):
    account_name = os.getenv('AZURE_ACCOUNT_NAME')
    account_key = None # On utilise la chaîne de connexion, donc la clé n'est pas nécessaire ici
    azure_container = os.getenv('AZURE_CONTAINER')
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    expiration_secs = None # Les fichiers seront accessibles en permanence