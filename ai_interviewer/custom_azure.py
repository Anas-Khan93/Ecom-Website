import os
from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name= env("AZURE_ACCOUNT_NAME")
    account_key= env("AZURE_ACCOUNT_KEY")
    azure_container= env('AZURE_CONTAINER')
    expiration_secs= None