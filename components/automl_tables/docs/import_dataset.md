
## Import dataset component
### Intended use
Use the component to import data from GCS or BigQuery to an AutoML Dataset.
### Runtime arguments

|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|project_id|GCP Project ID|GCPProjectID|No||
|region|AutoML Tables region. Currently, the only supported region is us=central1|String|No|us-central1|
|description|AutoML Tables Dataset description|String|No||
|source_data_uri|The location of the source data. For GCS locations it is a comma separated list of GCS URLs to CSV files. E.g. `"gs://bucket1/folder1/file1.csv,gs://bucket2/file2.csv"`. For a BigQuery location it is a URI to a BigQuery table. E.g. `"bq://project_id1/dataset_id1/table_id1"`|String|No||
|target_column_name|The name of a column in the source data to use as the training label.|String|Yes||
|weight_column_name|The name of a column in the source data to be used as the weight column|String|Yes||
|ml_use_column_name|The name of a column in the source data to be used to split the rows into TRAIN, VALIDATE, and TEST sets.|String|Yes||


### Output

|Name|Description|Type|
|----|-----------|----|
|project_id|GCP Project ID. This is a pass-through of the input project_id|GCPProjectID|
|output_dataset_id|The ID of the created AutoML Tables Dataset|String|
|output_location|The region where the AutoML Tables Dataset was created.|String|

### Description
The component is a wrapper around `AutoMlClient.create_dataset()` API. Currently, the component does not allow you to configure the schema of the target AutoML Tables Dataset. The component uses schema auto-detection.
