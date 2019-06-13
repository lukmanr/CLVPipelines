# Customer Lifetime Value Training and Inference Pipelines

This folder contains source code for two KFP Pipelines:
- Customer lifetime value training and deployment pipeline
- Customer lifetime value batch prediction pipeline


## CLV training and deployment pipeline
The training and deployment pipeline uses historical sales transactions data to train and optionally deploy a machine learning regression model. The model is trained to predict a value of future purchases for a customer, based on a history of previous purchases by this customer. For more information about modeling for customer lifetime value prediction refer to the  articles in  the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series.

### Pipeline design
The pipeline uses BigQuery for data preprocessing and feature engineering and AutoML Tables for model training and deployment.

The below diagram depicts the workflow implemented by the pipeline:


![Train and deploy](/images/train.jpg)

1. Load historical sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Prepare a BigQuery query. The query is generated from a query template and runtime arguments passed to the pipeline.
1. Execute a BigQuery query to create features from the historical sales transactions. The engineered features are stored in a BigQuery table.
1. Import features to an AutoML dataset.
1. Trigger AutoML model training.
1. After training completes, retrieve the model's evaluation metrics.
1. Compare the model's performance against the performance threshold.
1. If the model meets or exceeds the performance threshold deploy the model for online predictions.


### Runtime arguments

The pipeline accepts the following runtime arguments


Name | Type | Optional | Default | Description
-----|------|----------|---------|------------
project_id | GCProjectID | No | | The project to execute processing 
source_gcs_path | GCSPath | No | |The Cloud Storage path to the historical sales transaction data. Must be set to an empty string if source_bq_table is not empty.
source_bq_table | String | No | | The full id of a BigQuery table with historical sales transaction data. Must be set to an empty string if source_gcs_path is not empty.
bq_dataset_name | String | Yes | | The name of the persistent dataset to keep the sales transactions (if loaded from GCS) and feature tables. If the dataset does not exist, the pipeline will create a new one. If the dataset name not passed the pipeline will create a unique name. 
transactions_table_name | String | Yes | transactions | The name of the table to keep historical sales transactions data if loaded from GCS. Ignored if the source is BigQuery. If not passed the pipeline will create a unique name.
features_table_name | String | Yes | features | The name of the table to keep engineered features. If not passed the pipeline will create a unique name.
dataset_location | String | Yes | US | The location to create the dataset. 
threshold_date | Date (YYYY-MM-DD) | No | | The date that divides the input sales transactions into two groups. The transactions before the threshold are used to calculate the features. The transactions after the threshold and before the predict_end (inclusive) are used to calculate the monetary target. Refer to previous articles in the series for more information.
predict_end | Date (YYYY-MM-DD) | No|| The transactions between the threshold_date and the predict_end are used to calculate the monetary target. The period between the threshold_end and the predict_end is a customer value prediction period.
max_monetary | Integer |No||Customers with a calculated value higher than max_monetary are treated as outliers and not included in modeling.
aml_compute_region|String|Yes|us-central1|Compute region for Automl Tables. Currently, the only supported region is us-central1 and it is a default value of the argument.
aml_dataset_name|String|No|clv_features|The name of the AutoML Tables dataset where features are imported.
aml_model_name|String|No|clv_regression|The name of the AutoML Tables model
train_budget|Integer|Yes|1000|AutoML Tables train budget in millihours
target_column_name|String|No|target_monetary|The name of the column in the features dataset that will be used as a training label
features_to_exclude|List|Yes|[customer_id]| The list of features to exclude from training
optimization_objective|String|No|MINIMIZE_MAE| AutoML Tables optimization objective
primary_metric|String|No|mean_absolute_error|The primary metric to use as a decision for model deployment
deployment_threshold|Float|No|900|The performance threshold for the primary metric. If the value of the primary metric is lower than the deployment threshold the model is deployed
skip_deployment|Bool|No|True|The flag forcing skipping model deployment if set to True
query_template_uri|GCSPath|No||The GCS path to a BigQuery query template that converts historical transaction data to features. When deploying using Cloud Build the default value is set automatically

### Input schema
The pipeline requires the input data (historical sales transactions) to conform to the following schema. 

| Field | Type |
|-------|------|
| customer_id | string |
| order_date | date (yyyy-MM-dd) |
| quantity | integer |
| unit_price | float |

### Output schema

The feature engineering phase of the pipeline generates a BigQuery table with the following schema.

## Batch predict pipeline
Like the training pipeline, the batch predict pipeline uses historical sales transactions data as its input. The pipeline applies the trained CLV  model to generate customer lifetime value predictions.

### Pipeline design
The below diagram depicts the workflow implemented by the batch predict pipeline.
![Batch predict](/images/predict.jpg)

1. Load sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Execute a BigQuery query to create features from the sales transactions. The engineered features are stored in a BigQuery table.
1. Invoke AutoML Tables Batch Predict service to score the data.
1. AutoML Tables Batch Predict stores resulting predictions in either GCS or BigQuery

### Runtime arguments

The pipeline accepts the following runtime arguments


Name | Type | Optional | Default | Description
-----|------|----------|---------|------------
project_id | GCProjectID | No | | The project to execute processing 
source_gcs_path | GCSPath | No | |The Cloud Storage path to the historical sales transaction data. Must be set to an empty string if source_bq_table is provided.
source_bq_table | String | No | | The full id of a BigQuery table with historical sales transaction data. Must be set to an empty string if source_gcs_path is provided.
bq_dataset_name | String | Yes | | The name of the persistent dataset to keep the sales transactions (if loaded from GCS) and feature tables. If the dataset does not exist, the pipeline will create a new one. If the dataset name not passed the pipeline will create a unique name. 
transactions_table_name | String | Yes | transactions | The name of the table to keep historical sales transactions data if loaded from GCS. Ignored if the source is BigQuery. If not passed the pipeline will create a unique name.
features_table_name | String | Yes | features | The name of the table to keep engineered features. If not passed the pipeline will create a unique name.
dataset_location | String | Yes | US | The location to create the dataset. 
threshold_date | Date (YYYY-MM-DD) | No | | The date that divides the input sales transactions into two groups. The transactions before the threshold are used to calculate the features. The transactions after the threshold and before the predict_end (inclusive) are used to calculate the monetary target. Refer to previous articles in the series for more information.
predict_end | Date (YYYY-MM-DD) | No|| The transactions between the threshold_date and the predict_end are used to calculate the monetary target. The period between the threshold_end and the predict_end is a customer value prediction period.
max_monetary | Integer |No||Customers with a calculated value higher than max_monetary are treated as outliers and not included in modeling.
aml_compute_region|String|Yes|us-central1|Compute region for Automl Tables. Currently, the only supported region is us-central1 and it is a default value of the argument.
aml_model_id|String|No||The full ID  of the AutoML Tables model to use for inference.
destination_prefix|String|No||The URI prefix of the destination for predictions. `gs://[BUCKET]/[FOLDER]` for GCS destination. `bq://[YOUR_PROJECT_ID]` for BigQuery destination
query_template_uri|GCSPath|No||The GCS path to a BigQuery query template that converts historical transaction data to features. When deploying using Cloud Build the default value is set automatically




## Folder content
- `train_pipeline.py` - The training and deployment pipeline DSL
- `batch_predict.py` - The batch predict pipeline DSL
- `helper_components/helper_components.py` - Utility components used by the pipelines. Implemented as KFP Lightweight Python components
- `helper_components/Dockerfile` - A base image for utility components
- `artificats/query_template.sql.jinja` - The template for BigQuery SQL query used for data preprocessing
- `settings.yaml` - Default values for the pipelines parameters and compiler pragmas
