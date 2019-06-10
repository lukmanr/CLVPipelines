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

To install Kubeflow, including Kubeflow Pipelines on Google Kubernetes Engine follow the instructions on [www.kubeflow.org](https://www.kubeflow.org/docs/gke/deploy/).

Make sure to configure Identity Aware Proxy (IAP). Deploy [v0.5.1](https://github.com/kubeflow/kubeflow/releases) of Kubeflow.




## Training and deploying a Customer Lifetime Value prediction model
Training and deployment of a CLV model is orchestrated by a Kubeflow Pipeline that uses BigQuery for data preprocessing and feature engineering and AutoML Tables for model training and deployment. 





### Runtime arguments
The pipeline accepts the following runtime arguments:




The repository includes two subfolders: `pipelines` and `components`.

The `pipelines` folder contains the example pipelines that demonstrate how to utilize pre-built and custom **Kubeflow Pipelines Components** to orchestrate data preparation, model training, model deployment and inference. Refer to README files associated with each pipeline for more details.

The `components` folder contains:
- An example custom Kubeflow Pipeline Component. The component is a wrapper around **AutoML Tables API**.
- The definition of the base image used by Lightweight Python components used in some pipelines.

To run the pipelines you need to set up a Google Cloud Platform (GCP) project with the following GCP services enabled:
- Google Kubernetes Engine (GKE)
- BigQuery
- Dataproc
- Cloud Storage
- AutoML Tables (beta)

Refer to this [how-to-guide](https://cloud.google.com/apis/docs/enable-disable-apis) to enable the required services.

You are going to use [Cloud Shell](https://cloud.google.com/shell/) to configure the services used in the tutorial.

## Setting the default Project 
Connect to Cloud Shell and set the default **Project**  to the project you are going to use for the tutorial. To create a new project follow the [instructions](https://cloud.google.com/resource-manager/docs/creating-managing-projects).


```
gcloud config set project [your project ID]

```
## Configuring Kubeflow Pipelines on Google Kubernetes Engine

### Install Google Kubernetes Engine (GKE)
Create a single-zone **Standard** cluster. Make sure to replace the placeholders with your zone and cluster name. 

```
CLUSTERNAME=[your cluster name]
ZONE=[your zone]
gcloud beta container clusters create $CLUSTERNAME \
  --cluster-version '1.12.7-gke.10' --enable-autoupgrade \
  --zone $ZONE \
  --scopes cloud-platform \
  --enable-cloud-logging \
  --enable-cloud-monitoring 
```

Bind your account as a cluster admin.
```
kubectl create clusterrolebinding ml-pipeline-admin-binding --clusterrole=cluster-admin --user=$(gcloud config get-value account)
```

### Install Kubeflow Pipelines
The code samples in the tutorial have been developed for version 1.20 of KFP.
```
PIPELINE_VERSION=4eeeb6e22432ece32c7d0efbd8307c15bfa9b6d3
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$PIPELINE_VERSION/manifests/namespaced-install.yaml
```
It may take a couple of minutes for all services to start. To check the status of the pods:
```
kubectl get pods -n kubeflow
```

### Connect to Kubeflow Pipelines UI

To connect to KFP UI use Cloud Shell to forward a local port to KFP UI service. 
```
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
After port forwarding has been established, use Cloud Shell web preview to open KFP UI on port 8080. Note that it may take a couple of minutes before the UI is fully functional.

You are now ready to run the tutorial's pipelines using KFP UI.

## Running the pipelines using Kubeflow Pipelines UI

### Downloading the sample dataset
The input to the pipelines are customer transactions assembled in a CSV file(s) with the below schema. Refer to previous articles in CLV series to understand in more detail feature engineering and modeling techniques used in developing Customer Lifetime Value models.

| Field | Type |
|-------|------|
| customer_id | string |
| order_date | date (yyyy-MM-dd) |
| quantity | integer |
| unit_price | float |

The dataset used in the tutorial is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. You need to copy this file to a bucket in *your* project.

At this time AutoML Tables can only read from a regional bucket in the same region as AutoML Tables service. As of this writing, the only region supported by AutoML Tables is `us-central1`.

*For now we will make the bucket public. TBD - finalize security between GKE, KFP, AutoML, Dataproc and BigQuery.*

In a new Cloud Shell session.

```
BUCKET=[YOUR_BUCKET_NAME]
gsutil mb  -c regional -l us-central1 gs://$BUCKET
gsutil bucketpolicyonly set on gs://$BUCKET
gsutil iam ch allUsers:objectViewer gs://$BUCKET
```

Copy the sample dataset to the newly created bucket.
```
gsutil cp gs://clv-datasets/transactions/transactions.csv gs://$BUCKET/transactions/transactions.csv
```

### Running the sample pipelines

The pre-compiled pipelines can be found in the root of the `pipelines/compiled` folder. There are three pipelines:
- `clv_train_bq.tar.gz`
- `clv_train_dataproc.tar.gz`
- `clv_batch_predict.tar.gz`

The `clv_train_bq.tar.gz` pipeline goes through the following steps:
1. Load the sample transaction file from GCS to BigQuery table
1. Use BigQuery to engineer CLV features and store the features in a BigQuery table
1. Import the table with the features to an AutoML Tables dataset 
1. Train an AutoML Tables model
1. Retrieve and log (as a KFP artifact) regression evaluation metrics
1. Check MAE of the trained model against the threshold (passed as a parameter
1. If the trained model's MAE is lower than the threshold deploy the model

The `clv_train_dataproc.tar.gz` pipeline goes through the following steps:
1. Use a PySpark scrip to engineer CLV features from customer transactions. Both input (transactions) and output (features) are CSV files stored in GCS.
1. Import the table with the features to an AutoML Tables dataset 
1. Train an AutoML Tables model
1. Retrieve and log (as a KFP artifact) regression evaluation metrics
1. Check MAE of the trained model against the threshold (passed as a parameter
1. If the trained model's MAE is lower than the threshold deploy the model

The `clv_score_bq_automl.tar.gz` pipeline goes through the following steps:
1. Use a PySpark scrip to engineer CLV features from customer transactions. Both input (transactions) and output (features) are CSV files stored in GCS.
2. Use a trained AutoML Tables model to score feature files and store predictions in a BigQuery table.

The pipelines utilize SQL (`clv_train_bq.tar.gz`) and PySpark (`clv_train_dataproc.tar.gz` and `clv_batch_predict.tar.gz`) scripts. The pipelines expect to find the scripts in GCS location passed as one of the pipelines' parameters.

To upload the scripts into your GCS bucket.

```
gsutil cp [REPO_ROOT_FOLDER]/pipelines/src/scripts/* gs://$BUCKET/scripts
```

The pipelines accept a number of parameters that control their behaviour (TBD to describe parameters for each pipeline). The pipelines have been pre-configured with reasonable default for some of the parameters.

Feel free to experiment with different values for other parameters.

To run the pipeline. Using KFP GUI.
1. Upload the pipeline's `.tar.gz` file
2. Create a new experiment
3. Set the required parameters and create a new run

Depending on the value of the *train_budget* pipeline parameter, the training step may take up to a few hours. 


## Configuring a development environment

To re-build the tutorial's KFP components, customize and recompile the pipelines, or use a programmatic inteface to Kubeflow Pipelines, you need a development environment with the following configuration:
- Python 3.5+
- Python Fire package
- Docker client
- Kubeflow Pipelines SDK v 1.20
- gcloud SDK
- kubectl
- Access to your GCP project

You can use a platform of your choice as long as it meets the above requirements, including GCE VMs and GCP AI Platform Notebooks.

### Installing and configuring Kubeflow Pipelines SDK 

It is recommended to install KFP SDK to a dedicated Python or Conda environment. The environment must be based on Python 3.5 or higher.

To install KFP SDK v0.1.20 run the following command:
```
SDK_VERSION=0.1.20
python3 -m pip install https://storage.googleapis.com/ml-pipeline/release/$SDK_VERSION/kfp.tar.gz --upgrade
```

### Installing Python Fire

To install Python Fire
```
python3 -m pip install fire
```


### Configure port forwarding to Kubeflow Pipelines service 
If you want to submit Kubeflow Pipelines runs programmatically (rather than through GUI) you need access to the `ml-pipeline` service that is running on your GKE cluster. By default the service is not exposed on a public IP address. For the purpose of this tutorial, you access the service using port forwarding. Alternatively, you can expose the service through an external IP.

To configure access to your GKE cluster.

```
gcloud container clusters get-credentials [YOUR_CLUSTER_NAME] --zone [YOUR_ZONE]
```

To configure port forwarding to `ml-pipeline`.

```
kubectl port-forward -n kubeflow svc/ml-pipeline 8082:8888
```

Note that you can use other ports than 8082.

Make sure that the terminal window stays open and the command is running when you submit the jobs using KFP SDK client API.


## Rebuilding the components and recompiling the pipelines
Follow the instructions in the README files in `pipelines` and `components` subfolders if you want to rebuild the components and/or recompile the pipelines.




