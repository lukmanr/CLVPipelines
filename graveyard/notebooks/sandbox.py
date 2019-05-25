#%%

from google.cloud import automl_v1beta1 as automl


project_id = 'sandbox-235500'
location = 'us-central1'

client = automl.AutoMlClient()
location_path = client.location_path(project_id, location)

dataset_ref = client.create_dataset(
        location_path,
        {
            "display_name": 'test',
            "description": 'test',
            'tables_dataset_metadata': {}
        })  

#%%

#input_uris = ['gs://clv-datasets/order-summaries/part-0.csv', 'gs://clv-datasets/order-summaries/part-1.csv']
input_config = {"gcs_source": {"input_uris": input_uris}}

response = client.import_data(dataset_ref.name, input_config)
    # Wait for import to complete
response.result()    

#%%

from google.cloud import storage

storage_client = storage.Client()

bucket_name = 'clv-datasets'
prefix = 'order-summaries'
delimiter = ''

bucket = storage_client.get_bucket(bucket_name)


blobs = bucket.list_blobs(prefix=prefix, delimiter=delimiter)
# blobs = bucket.list_blobs()

print('Blobs:')
for blob in blobs:
     print(blob.name)

#%%
import re
from google.cloud import storage

storage_client = storage.Client()

source_gcs_folder = 'gs://clv-pipelines/order-summaries/'
_, bucket_name, prefix = re.split("gs://|/", source_gcs_folder, 2)
prefix = prefix + '/' if prefix[-1] != '/' else prefix
bucket = storage_client.get_bucket(bucket_name)
blobs = [blob.name for blob in bucket.list_blobs(prefix=prefix, delimiter=delimeter) 
    if (blob.name != prefix) and not (blob.name.endswith('_SUCCESS'))]

blobs = ','.join(blobs)


#%%

import re

re.search('es$', 'order-summaries')

#%%

#%%

from google.cloud import storage