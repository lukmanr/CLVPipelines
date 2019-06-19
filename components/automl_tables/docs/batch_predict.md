## Batch Predict
### Intended use
Use the component to run batch predict job using a trained AutoML model.

|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|project_id|GCP Project ID|GCPProjectID|No||
|region|AutoML Tables region. Currently, the only supported region is us=central1|String|No|us-central1|
|source_data_uri|The location of the source data to be scored. For GCS locations it is a comma separated list of GCS URLs to CSV files. E.g. `"gs://bucket1/folder1/file1.csv,gs://bucket2/file2.csv"`. For a BigQuery location it is a URI to a BigQuery table. E.g. `"bq://project_id1/dataset_id1/table_id1"`|String|No||
|destination_prefix|The prefix of the destination where to store predictions. For GCS should be `"gs://[bucket_name]/[folder_name]"`. For BigQuery should be `"bq://[Project ID]"`|String|No||


### Output

|Name|Description|Type|
|----|-----------|----|
|output_destination|The URL of the destination where the predictions are stored. For GCS it is `"gs:[bucket_name]/[folder_name]/[predictions_folder]". For BigQuery it is "[project_id].[dataset_name].[table_name]".|String|

### Description
The component is a wrapper around `AutoMlClient.batch_predict()` API. 
