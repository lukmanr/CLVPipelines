This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value (CLV) model training and deployment with Kubeflow Pipelines (KFP)**. 

**NOTE**. *The reminder of this README is a draft of the tutorial article that will be published into the solutions section on google.com. After the article is published, the README will be edited to remove duplicate information*


The tutorial is the fifth part of the series Predicting Customer Lifetime Value with AI Platform. It demonstrates how to operationalize Customer Lifetime Value model training, deployment and inference using Kubeflow Pipelines (KFP) on Google Kubernetes Engine (GKE). Refer to the [previous articles](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) in the series for more information on Customer Lifetime Value concepts and modeling techniques. 

The pipelines used in the tutorial follow the data pre-processing, training and scoring flow that is similar to one described in [Part 4 of the series](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-automl-tables) :
- BigQuery is used for data cleansing and feature engineering, and
- AutoML Tables is used for model training, deployment, and scoring.

In the first part of the tutorial you:
- Install Kubeflow Pipelines on Google Kubernetes Engine
- Configure and deploy two template pipelines:
  - The training and deploymnet pipeline
  - The batch predict pipeline
- Run the pipelines using Kubeflow Pipelines UI

In the second part of the tutorial you learn how to:
- Customize the pipelines
- Customize the deployment process
- Trigger pipeline runs using Kubeflow Pipelines SDK

The tutorial assumes that you have a basic understanding of the following GCP concepts and services:
- GCP Projects
- Cloud Shell
- Cloud Storage
- BigQuery
- Google Kubernetes Engine
- AutoML Tables
- Cloud Build

In addition, you need to familiarize yourself with the key Kubeflow and Kubeflow Pipelines concepts as described on [www.kubeflow.org](http://www.kubeflow.org).

## Objectives
- Gain hands-on experience with setting up Kubeflow Pipelines runtime environment on Google Kubernetes Engine
- Understand how to architect KFP pipelines that orchestrate Google Cloud managed services.
- Learn how to automate deployment of pipelines, pipeline components, and pipeline artifacts.
- Learn how to schedule and execute pipelines using both Kubeflow Pipelines UI and KFP SDK APIs.
- Understand how to customize KFP pipelines

## Costs
This tutorial uses billable components of Google Cloud Platform, including:
- Google Kubernetes Engine
- Cloud Storage
- BigQuery
- AutoML Tables
- Cloud Build

You can use the Pricing Calculator to generate a cost estimate based on your projected usage.

## Before you begin
1. Select or create a GCP project.
1. Enable billing for you project
1. Enable the following Cloud APIs:
- Compute Engine
- Cloud Storage
- Container Registry
- BigQuery
- Kubernetes Engine
- Cloud Build
- Deployment Manager
- Identity and Access Management
- AutoML


## Installing Kubeflow Pipelines on Google Kubernetes Engine

The runtime environment that you set up and use in the tutorial is depicted on the below diagram:
![KFP Runtime](/images/architecture.jpg)

The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running Google Cloud Platform. The pipelines access **Cloud Storage**, **BigQuery**, and **AutoML Tables** services through KFP components that wrap Cloud APIs. The container images for the components are managed in **Container Registry**.

**NOTE**. *The below installation procedure installs a full Kubeflow configuration that includes Kubeflow Pipelines and other components. By the end of June, a lightweight configuration that only includes Kubeflow Pipeline components will be supported. At that time the tutorial will be updated to support the lightweight configuration.*

### Using Deployment Manager to install Kubeflow on GCP
To install Kubeflow, including Kubeflow Pipelines on Google Kubernetes Engine follow the instructions on [www.kubeflow.org](https://www.kubeflow.org/docs/gke/deploy/).

**Make sure to configure Identity Aware Proxy (IAP)**. Deploy [v0.5.1](https://github.com/kubeflow/kubeflow/releases) of Kubeflow.

For educational purposes, it is recommended to go through [Deploy using CLI](https://www.kubeflow.org/docs/gke/deploy/deploy-cli/).

Note that it make take up to an hour to complete the installation.

## Building and deploying the pipelines
Before the tutorial's pipelines can be run, they have to be configured, compiled, and deployed in your project.

The building and deploying process have been automated using [GCP Cloud Build](https://cloud.google.com/cloud-build/docs/).  The build config file can be found in `/cloud-build` folder of this repo. The build process goes through the following steps:
1. Copy the solution's github repo into the Cloud Build runtime environment
1. Create a docker image to support custom build steps
1. Build a base image for the pipeline's helper components (refer to the later sections to understand the pipeline's design). The name of the image is provided as a build parameter.
1. Build an image that hosts components wrapping AutoML Tables API. The name of the image is provided as a build parameter.
1. Update the YAML specifications of the AutoML Tables components with the name of the image created in the previous step
1. Update the settings that control the pipelines' compilation. The values for these settings are provided as build parameters.
1. Compile the pipelines. 
1. Deploy the compiled pipelines to a GCS folder in your project. The path to the folder is provided as a build parameter.
1. Deploy the artifacts used by the pipelines at runtime to a GCS folder in your project. The path to the folder is provided as a build parameter.
1. Deploy the component images to the Container Registry of your project. 
1. Copy the sample dataset to a GCS folder in your project. The path to the folder is provided as a build parameter.

You can submit the build process using the `gcloud builds submit` command. The build has been configured to accept as a set of configuration parameters. The values for these parameters can be set when submitting the build job using the `--substitutions` option of the `gcloud builds submit` command. The following parameters are required:





Parameter | Description 
-----------|-------------
_CLV_REPO  | The name of the tutorial's github repository. 
_BASE_IMAGE | The name of the image that is used by lightweight Python compoments. Specify the image name only. The image will be pushed to `gcr.io/[YOUR_PROJECT_ID]/[_BASE_IMAGE]`
_AUTOML_TABLES_IMAGE | The name of the image that hosts AutoML Tables components
_TRAIN_PIPELINE | The name for the compiled training pipeline. The compiled pipeline will be saved as `[_TRAIN_PIPELINE].tar.gz`
_PREDICT_PIPELINE | The name for the compiled training pipeline. The compiled pipeline will be saved as `[_PREDICT_PIPELINE].tar.gz` |
_BUCKET_NAME | The name of the bucket in your project to store artifacts used by the pipelines' at runtime. If the bucket does not exist, it will be created by the build 
_PIPELINES_FOLDER | The name of the folder in _BUCKET_NAME to store the compiled pipelines
_ARTIFACTS_FOLDER | The name of the folder in _BUCKET_NAME to store artificats used by the pipelines at running time. 
_SAMPLE_DATASET_FOLDER | The name of the folder in _BUCKET_NAME to store the sample dataset used by the pipelines.


The `/cloud-build/build.sh` demonstrates how to use `gcloud builds submit` to start the build process. 


To build and deploy the pipelines:
1. Open [Cloud Shell](https://cloud.google.com/shell/docs/) in your project.
2. Create a working directory and download build configuration
```
cd
mkdir [DIRECTORY_NAME]
cd [DIRECTORY_NAME]
wget https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/cloud-build/cloudbuild.yaml
wget https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/cloud-build/build.sh
```
3. Update `build.sh` with your parameter values
4. Start the build
```
chmod 755 build.sh
./build.sh
```

## Running the pipelines using Kubeflow Pipelines UI
### Running the CLV Training and Deployment pipeline

The CLV training and deployment pipeline uses historical sales transactions data to train and optionally deploy a machine learning regression model. The model is trained to predict a total value of future purchases in a given timeframe, based on a history of previous purchases. For more information about modeling for customer lifetime value prediction refer to previous articles in [the series](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro).

The below diagram depicts the workflow implemented by training and deployment pipeline.

#### Training and deployment workflow

![Train and deploy](/images/train.jpg)

1. Load historical sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Execute a BigQuer query to create features that will be used for model training. The engineered features are stored in a BigQuery table.
1. Import features to an AutoML dataset.
1. Trigger AutoML model training.
1. After training completes, retrieve model evaluation metrics.
1. Compare the model performance (a value of the primary metric passed as the pipeline’s parameter) against the performance threshold.
1. If the trained model meets or exceeds the performance threshold deploy the model for online predictions.

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


#### Uploading and starting the pipeline
To run the pipeline using Kubeflows Pipelines UI:
- Connect to Kubeflow Pipelines UI. If you deployed Kubeflow using the Deployment Manager the Kubeflow Dashboard is available at `https:[DEPLOYMENT_NAME].endpoints.[YOUR_PROJECT_ID].cloud.goog`. The Kubeflow Pipelines UI is accessible from the Kubeflow Dashboard.
- Upload the compile pipeline's `.tar.gz` file. The file can be found in a GCS path configured during the build process
- Configure the experiment and run the pipeline following the procedure described in [Kubeflow Pipelines Quickstart](https://www.kubeflow.org/docs/pipelines/pipelines-quickstart). Set the required parameters and if required change the default values.


### Running the CLV Batch Predict pipeline

Like the training pipeline, the batch predict pipeline uses historical sales transactions data as its input. The pipeline applies a trained CLV regression model to generate customer lifetime value predictions.

The below diagram depicts the workflow implemented by the batch predict pipeline.

#### Batch predict workflow

![Batch predict](/images/predict.jpg)

1. Load historical sales transactions from Cloud Storage to a  BigQuery staging table. If the data are already in BigQuery this step is skipped.
1. Execute a BigQuery query to create features that will be used by the model. The engineered features are stored in a BigQuery table.
1. Invoke AutoML Tables Batch Predict.
1. AutoML Tables Batch Predict stores predictions in either GCS or BigQuery

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
aml_model_id|String|No||The full ID  of the AutoML Tables model to use for inference.
destination_prefix|String|No||The URI prefix of the destination for predictions. `gs://[BUCKET]/[FOLDER]` for GCS destination. `bq://[YOUR_PROJECT_ID]` for BigQuery destination
query_template_uri|GCSPath|No||The GCS path to a BigQuery query template that converts historical transaction data to features. When deploying using Cloud Build the default value is set automatically



#### Uploading and starting the pipeline
To run the pipeline using Kubeflows Pipelines UI:
- Connect to Kubeflow Pipelines UI. If you deployed Kubeflow using the Deployment Manager the Kubeflow Dashboard is available at `https:[DEPLOYMENT_NAME].endpoints.[YOUR_PROJECT_ID].cloud.goog`. The Kubeflow Pipelines UI is accessible from the Kubeflow Dashboard.
- Upload the compile pipeline's `.tar.gz` file. The file can be found in a GCS path configured during the build process
- Configure the experiment and run the pipeline following the procedure described in [Kubeflow Pipelines Quickstart](https://www.kubeflow.org/docs/pipelines/pipelines-quickstart). Set the required parameters and if required change the default values.



## Running the pipelines using KFP SDK API


