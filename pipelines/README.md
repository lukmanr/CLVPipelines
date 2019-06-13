# Customer Lifetime Value Pipelines

This folder contains source code for two KFP Pipelines:
- Train and deploy
- Batch predict

Folder content

- `train_pipeline.py` - The training and deployment pipeline DSL
- `batch_predict.py` - The batch predict pipeline DSL
- `helper_components/helper_components.py` - Utility components used by the pipelines. Implemented as KFP Lightweight Python components
- `helper_components/Dockerfile` - A base image for utility components
- `artificats/query_template.sql.jinja` - The template for BigQuery SQL query used for data preprocessing
- `settings.yaml` - Default values for the pipelines parameters and compiler pragmas

## Training and deployment pipeline
The below diagram depicts the workflow implemented by the training and deployment pipeline

![Train and deploy](/images/train.jpg)

1. Load historical sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Execute a BigQuery query to create features from the historical sales transactions. The engineered features are stored in a BigQuery table.
1. Import features to an AutoML dataset.
1. Trigger AutoML model training.
1. After training completes, retrieve the model's evaluation metrics.
1. Compare the model's performance against the performance threshold.
1. If the model meets or exceeds the performance threshold deploy the model for online predictions.

The pipeline accepts the following runtime arguments

#### Runtime arguments

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

#### Input schema
The pipeline requires the input data (historical sales transactions) to conform to the following schema. In the second part of the tutorial you learn how to customize the pipeline to digest data in other schemas.


| Field | Type |
|-------|------|
| customer_id | string |
| order_date | date (yyyy-MM-dd) |
| quantity | integer |
| unit_price | float |

The sample dataset used in the tutorial is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. The build script copies this file to a GCS folder in your project.

