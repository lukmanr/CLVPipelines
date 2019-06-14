
## Import dataset component
### Intended use
Use the component to import data from GCS or BigQuery to an AutoML Dataset.
### Runtime arguments
|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|project_id|GCP Project ID|GCPProjectID|No||
|region|AutoML Tables region. Currently, the only supported region is us=central1|String|No|us-central1|
|description|AutoML Tables Dataset description|String|No||
|source_data_uri|The location of the source data. For GCS locations it is a comma separated list of GCS URLs to CSV files. E.g. `gs://bucket1/folder1/file1.csv,gs://bucket2/file2.csv`. For BigQuery location it is a URI to a BigQuery table. E.g. `bq://project_id1/dataset_id1/table_id1`|String|No||


### Output
### Cautions & requirements
### Implementation Details
