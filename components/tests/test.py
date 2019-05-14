#%%
import sys

sys.path

#%%
import kfp
import clv_components as clv


#%%
project_id = 'sandbox-235500'
data_source_id = 'sandbox-235500.CLVDataset.transactions'
dest_dataset_id = 'CLVDataset'
dest_table_id = 'test'
threshold_date = '2011-08-08'
predict_end = '2011-12-12'
max_monetary = '15000'
query_template_uri = 'gs://sandbox-235500/sql-templates/create_features.sql'

prepare_features_result = clv.prepare_features(
        project_id=project_id,
        data_source_id=data_source_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        dest_dataset_id=dest_dataset_id,
        dest_table_id=dest_table_id,
        query_template_uri=query_template_uri
        )

#%%

dataset_ref = clv.import_dataset(
    project_id = 'sandbox-235500',
    compute_region = 'us-central1',
    dataset_name = 'clv_test',
    source_data = 'bq://sandbox-235500.CLVDataset.test')

print(dataset_ref)