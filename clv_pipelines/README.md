# Customer Lifetime Value Training and Inference Pipelines

This folder contains source code for two KFP Pipelines:
- The CLV training and deployment pipeline
- The CLV batch prediction pipeline


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
bq_dataset_name | String | Yes | | The name of the persistent dataset to keep the sales `transactions` (if loaded from GCS) and `features` tables. If the dataset does not exist, the pipeline will create a new one. If the dataset name not passed the pipeline will create a unique name. 
transactions_table_name | String | Yes | transactions | The name of the table to keep historical sales transactions data if loaded from GCS. Ignored if the source is BigQuery. If not passed the pipeline will create a unique name.
features_table_name | String | Yes | features | The name of the table to keep engineered features. If not passed the pipeline will create a unique name.
dataset_location | String | Yes | US | The location to create the dataset. 
threshold_date | Date (YYYY-MM-DD) | No | | The date that divides the input sales transactions into two groups. The transactions before the threshold are used to calculate the features. The transactions after the threshold and before the predict_end (inclusive) are used to calculate the monetary target. Refer to previous articles in the series for more information.
predict_end | Date (YYYY-MM-DD) | No|| The transactions between the threshold_date and the predict_end are used to calculate the monetary target. The period between the threshold_end and the predict_end is a customer value prediction period.
max_monetary | Integer |No||Customers with a calculated value higher than max_monetary are treated as outliers and not included in modeling.
aml_compute_region|String|Yes|us-central1|A compute region for Automl Tables. Currently, the only supported region is us-central1 and it is a default value of the argument.
aml_dataset_name|String|No|clv_features|The name of an AutoML Tables dataset where features are imported.
aml_model_name|String|No|clv_regression|The name of an AutoML Tables model
train_budget|Integer|Yes|1000|AutoML Tables train budget in millihours
target_column_name|String|No|target_monetary|The name of a column in the AutoML dataset that will be used as a training label.
features_to_exclude|List|Yes|[customer_id]| A list of features to exclude from training.
optimization_objective|String|No|MINIMIZE_MAE| AutoML Tables optimization objective
primary_metric|String|No|mean_absolute_error|A primary metric to use as a decision for model deployment
deployment_threshold|Float|No|900|A performance threshold for the primary metric. If the value of the primary metric is lower than the deployment threshold the model is deployed
skip_deployment|Bool|No|True|Mode deployment is skipped if set to True
query_template_uri|GCSPath|No||A GCS path to a BigQuery query template that converts historical transaction data to features. When deploying using Cloud Build the default value is set automatically

### Sales transactions input schema
The pipeline requires the input data (historical sales transactions) to conform to the following schema. 

| Field | Type | Description |
|-------|------|-------------|
| customer_id | string | A unique customer ID |
| order_date | date (yyyy-MM-dd) | The date of a transaction. Transactions (potentially from multiple invoices) are grouped by day |
| quantity | integer | A number of items of a single SKU in a transaction |
| unit_price | float | A unit price of a SKU |

### Features schema

The feature engineering phase of the pipeline generates a BigQuery table with the following schema.

The timeline before the threshold date is refered to as *features period*.
The timeline between the threshold date and the predict end is refered to as *predict period*.


| Field | Type | Description |
|-------|------|-------------|
| customer_id | String | A unique customer ID |
| monetary | Float | The total spend by a customer in the features period|
| frequency | Integer | The number of transactions placed by a customer in the features period |
| recency | Integer |  The time (in days) between the first and the last orders in the features period |
| T | Integer | The time between the first order placed and in the features period |
| time_between | Float |  The average time betwee orders in the features period |
| avg_basket_value | Float |  The averate monetary value of the customer's basket in the features period |
| avg_basket_size | Float |  The average number of items in a basket in the features perio|
| cnt_returns | Integer |  The number of returns in the features period|
| target_monetary | Float | The total amount spent in the predict period. This is the label for predictions|


### Implementation details
#### Data preprocessing and feature engineering
The pipeline uses a custom **Load transactions** component - implemented as a [ligthweight Python compoment](https://www.kubeflow.org/docs/pipelines/sdk/lightweight-python-components/) - to check for the location of the input dataset with sales transactions. If the input dataset is in GCS, **Load transactions** moves the data to a staging table in BigQuery. If the input dataset is already in BigQuery **Load transactions** moves on.

Another [ligthweight Python compoment](https://www.kubeflow.org/docs/pipelines/sdk/lightweight-python-components/) - **Prepare query** - loads a sql query template and substitutes placeholders in the template with the values passed to it as runtime parameters. The template location is also passed as a runtime parameter. The automated build process automatically sets the default value of the template location to the GCS URL where the template was deployed. The template is encoded using [Jinja2](http://jinja.pocoo.org/) format and **Prepare query** uses **Jinja2** library to substitue placeholders.

The finalized query is passed to the standard [BigQuery component](https://aihub.cloud.google.com/u/0/p/products%2F4700cd7e-2826-4ce9-a1ad-33f4a5bf7433) component that converts input sales transactions in [input schema](#sales-transactions-input-schema) to features in [output schema](#features-schema) and stores the engineered features into a BigQuery table.

#### Model training
The next steps in the pipeline use the custom AutoML Tables components (refer to `/automl-tables-components for implementation details) to import the features table to AutoML Tables, configure the resulting AutoML Tables dataset, and trigger model training. The CLV Prediction is a regression task so the AutoML Tables regression model is trained.

#### Model deployment
After the training step completes, the pipeline retrieves the trained model's evaluation metrics and compares the value of the primary metric to the threshold value. Both the primary metric name and the threshold value are passed as the pipeline's runtime arguments. If the performance of the trained model exceeds the threshold value the model is deployed as an AutoML Tables deployment.

## CLV Batch predict pipeline

### Pipeline design

The pipeline uses the same pre-processing and feature engineering steps as the training pipeline. AutoML Tables Predict is used for batch predictions.

The below diagram depicts the workflow implemented by the pipeline:


### Pipeline design
The below diagram depicts the workflow implemented by the batch predict pipeline.
![Batch predict](/images/predict.jpg)

1. Load historical sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Prepare a BigQuery query. The query is generated from a query template and runtime arguments passed to the pipeline.
1. Execute a BigQuery query to create features from the historical sales transactions. The engineered features are stored in a BigQuery table.
1. Invoke AutoML Tables Batch Predict service to score the data.
1. AutoML Tables Batch Predict stores resulting predictions in either GCS or BigQuery

### Runtime arguments

The pipeline accepts the following runtime arguments


Name | Type | Optional | Default | Description
-----|------|----------|---------|------------
project_id | GCProjectID | No | | The project to execute processing 
source_gcs_path | GCSPath | No | |The Cloud Storage path to the historical sales transaction data. Must be set to an empty string if source_bq_table is provided.
source_bq_table | String | No | | The full id of a BigQuery table with historical sales transaction data. Must be set to an empty string if source_gcs_path is provided.
bq_dataset_name | String | Yes | | The name of the persistent dataset to keep the sales `transactions` (if loaded from GCS) and `features` tables. If the dataset does not exist, the pipeline will create a new one. If the dataset name is not passed the pipeline will create a unique name. 
transactions_table_name | String | Yes | transactions | The name of the table to keep historical sales transactions data if loaded from GCS. Ignored if the source is BigQuery. If not passed the pipeline will create a unique name.
features_table_name | String | Yes | features | The name of the table to keep engineered features. If not passed the pipeline will create a unique name.
dataset_location | String | Yes | US | The location to create the dataset. 
threshold_date | Date (YYYY-MM-DD) | No | | The date that divides the input sales transactions into two groups. The transactions before the threshold are used to calculate the features. The transactions after the threshold and before the predict_end (inclusive) are used to calculate the monetary target. Refer to previous articles in the series for more information.
predict_end | Date (YYYY-MM-DD) | No|| The transactions between the threshold_date and the predict_end are used to calculate the monetary target. The period between the threshold_end and the predict_end is a customer value prediction period.
max_monetary | Integer |No||Customers with a calculated value higher than max_monetary are treated as outliers and not included in modeling.
aml_compute_region|String|Yes|us-central1|A compute region for Automl Tables. Currently, the only supported region is us-central1 and it is a default value of the argument.
aml_model_id|String|No||The full ID  of the AutoML Tables model to use for inference.
destination_prefix|String|No||The URI prefix of the destination for predictions. `gs://[BUCKET]/[FOLDER]` for GCS destination. `bq://[PROJECT_ID]` for BigQuery destination
query_template_uri|GCSPath|No||The GCS path to a BigQuery query template that converts historical transaction data to features. When deploying using Cloud Build the default value is set automatically




### Implementation details
The pipeline uses the same data preprocessing and feature engineering flow as the training pipeline. After the features are generated and stored in a BigQuery table, the pipeline triggers batch scoring by invoking AutoML Batch Predict component. The output - CLV predictions - is stored in GCS or BigQuery. The output destination is passed as the pipeline's runtime parameter.


## Customizing the pipelines

Both the training and the batch predict pipeline can be customized at three levels:
- Fine tuning of the YAML settings file
- Modyfing data preprocessing and feature engineering logic
- Recoding the workflow

### Modifying the YAML settings file
The pipelines have been designed to minimize hard-coded values. Most pipeline settings are centralized in a single settings file - `settings.yaml`. The file uses the YAML format and has two sections:
- `argument_defaults`
- `compiler_settings`

In the `argument_defaults` section, you can define the default values for the pipelines' runtime arguments. In the `compiler_settings` section you define the settings that control how the KFP `dsl-compiler` converts Python DSL into the resulting YAML. Currently, the following `compiler_settings` are supported:
- `lightweight_components_base_image` - the full name of a container image used to run helper lightweight Python components
- `local_search_path` - a (YAML encoded) list of local file system paths that the DSL compiler searches to find component specfications
- `url_search_prefixes` - a (YAML encoded ) list of URL prefixes that the DSL compiler searches to find component specifications
- `use_sa_secret` - If set to True the pipelines will be compiled to use the KFP user service account to access external resources. Otherwise the pipelines will be compiled to use the default GCE service account of GKE nodes to access external resources.

To take effect, the `settings.yaml` file must be located in the directory from which the KFP `dsl-compiler` is invoked. 

### Modyfing data preprocessing and featuring engineering logic

The data preprocessing and feature engineering logic is encapsulated in a SQL query template. As described in the previous section, during a pipeline's run the template is converted into a BigQuery SQL query and submitted for execution by the **Prepare query** and **BigQuery** components. 

If a different logic needs to be implemented - for example new input columns, new features or a different logic for existing features - the SQL template and **Prepare query** components can be modified.

The pipelines use a very flexible approach when passing features to the training steps of the workflow. The AutoML Tables Import Dataset component can import any schema as long a label feature has the `Float` data type. Furthermore, the AutoML Tables Train Model component can be instructuted (through a runtime parameter) what features to use for training. As such no modifications to the training and deployment or batch predict part of the workflow are required when fine tuning the data preprocessing and feature engineering query template.


### Modifying the workflow

If a workflow implemented by a pipeline needs to be modified - for example, the expression used to decided whether and when to deploy a trained model needs to be fine tuned  - the pipeline's DSL can be re-coded.


