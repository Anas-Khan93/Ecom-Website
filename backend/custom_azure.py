from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    aacount_name= 'ecomimage'
    account_key= '1mu85ovEvWpOJySN4yZgjhIKyDXc3cDQ58NjYxzOSPKqiXQYGGKiXbYwz0GzUEM9hs1KTUzVFsnb+AStKIqzyQ=='
    azure_container= 'media'
    expiration_secs= None