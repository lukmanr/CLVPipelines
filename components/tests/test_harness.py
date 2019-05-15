#%%
%load_ext autoreload
%autoreload 2


#%%
import kfp
import clv_components as clv


#%%
project_id = 'sandbox-235500'
data_source_id = 'sandbox-235500.CLVDataset.transactions'
dest_dataset_id = 'CLVDataset'
dest_table_id = 'clv_features'
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

#%%

result = clv.train_model(
    project_id='sandbox-235500',
    location='us-central1',
    dataset_id='TBL7690257003549032448',
    model_name='clv_test_model',
    train_budget_milli_node_hours=1000,
    optimization_objective='MINIMIZE_MAE',
    target_column_name='target_monetary',
    feature_column_names=None
)


#%%
client = automl.AutoMlClient()

# Retrieve a table spec for the primary table
dataset_path='projects/165540728514/locations/us-central1/datasets/TBL7690257003549032448'
dataset_ref = client.get_dataset(dataset_path)
table_specs = client.list_table_specs(
    parent=dataset_path, 
    filter_='name="blabla"'
)
primary_table_spec = next(iter(table_specs))
print(primary_table_spec)


#%%

