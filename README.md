This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value model training and deployment with Kubeflow Pipelines**. The tutorial is the fifth part of the series [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro).
The fifth part focuses on demonstrating how to operationalize model training, deployment, and inference using Kubeflow Pipelines on Google Kubernetes Engine.

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

The pre-compiled pipelines can be found in the root of the `pipelines` folder. There are three pipelines:
- `clv_train_bq_automl.tar.gz`
- `clv_train_dataproc.tar.gz`
- `clv_score_bq_automl.tar.gz`

The `clv_train_bq_automl.tar.gz` pipeline goes through the following steps:
1. Load the sample transaction file from GCS to BigQuery table
1. Use BigQuery to engineer CLV features and store the features in a BigQuery table
1. Import the table with the features to an AutoML Tables dataset 
1. Train an AutoML Tables model
1. Retrieve and log (as a KFP artifact) regression evaluation metrics
1. Check MAE of the trained model against the threshold (passed as a parameter
1. If the trained model's MAE is lower than the threshold deploy the model

The `clv_train_dataproc_automl.tar.gz` pipeline goes through the following steps:
1. Load the sample transaction file from GCS to Spark Dataframe (on Dataproc)
1. Use PySpark to engineer CLV features and store the features as a CSV file on GCS
1. Import the table with the features to an AutoML Tables dataset 
1. Train an AutoML Tables model
1. Retrieve and log (as a KFP artifact) regression evaluation metrics
1. Check MAE of the trained model against the threshold (passed as a parameter
1. If the trained model's MAE is lower than the threshold deploy the model

The `clv_score_bq_automl.tar.gz` pipeline goes through the following steps:
TBD

The pipelines accept a number of parameters that control their behaviour (TBD to describe parameters for each pipeline). The pipelines have been pre-configured with reasonable defaults. The only two required parameters are: **Your project ID** and **GCS path** to the location of the sample dataset you downloaded in the previous steps.

Feel free to experiment with different values for other parameters.

To run the pipeline. Using KFP GUI.
1. Upload the pipeline's `.tar.gz` file
2. Create a new experiment
3. Set the required parameters and create a new run

Depending on the value of the *train_budget* pipeline parameter, the training step may take up to a few hours. 




## Configuring a development environment

To re-build the tutorial's KFP components, customize and recompile the pipelines, or use a programmatic inteface to Kubeflow Pipelines, you need a development environment with the following configuration:
- Python 3.5+
- Docker
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




