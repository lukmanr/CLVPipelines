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
Connect to Cloud Shell and set the default **Project**  to the project you are going to use for the tutorial. To create a new projec follow the [instructions](https://cloud.google.com/resource-manager/docs/creating-managing-projects).


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
The pipelines expect source training and scoring data with the below schema. Refer to previous articles in CLV series to understand in more detail feature engineering and modelling techniques used in developing Customer Lifetime Value models.

| Field | Type |
|-------|------|
| customer_id | string |
| order_date | date (yyyy-MM-dd) |
| quantity | integer |
| unit_price | float |

The dataset used in the tutorial is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. You need to copy this file to a public bucket in *your* project.

#### Create a regional GCS bucket
At this time AutoML Tables can only read from a regional bucket in the same region as AutoML Tables service. As of this writing, the only region supported by AutoML Tables is `us-central1`.

*For now we will make the bucket public. TBD - finalize security between GKE, KFP, AutoML, Dataproc and BigQuery.*

In a new Cloud Shell session.

```
gsutil mb  -c regional -l us-central1 gs://[YOUR_BUCKET_NAME]
gsutil bucketpolicyonly set on gs://[YOUR_BUCKET_NAME]
gsutil iam ch allUsers:objectViewer gs://[YOUR_BUCKET_NAME]


Copy the the sample dataset to the newly created bucket.
```
gsutil cp gs://clv-datasets/transactions/transactions.csv gs://[YOUR_BUCKET_NAME]/transactions
```


## Configuring a development environment

To re-build the tutorial's KFP components, recompile the pipelines, or use a programmatic inteface to Kubeflow Pipelines, you need a development environment with the following configuration:
- Python 3.5+
- Docker
- Kubeflow Pipelines SDK v 1.20
- gcloud SDK
- Access to your GCP project

The following instructions show how to configure Cloud Shell as the development environment. Note that you can use an environment of your choice as long as it meets the above requirements.


### Install and configure Kubeflow Pipelines SDK on Cloud Shell
Docker, gcloud SDK and Python 3.5.3 are pre-installed on Cloud Shell. The only missing component is KFP SDK.


To install KFP SDK v0.1.20 open a new Cloud Shell session and run the following command:
```
SDK_VERSION=0.1.20
python3 -m pip install https://storage.googleapis.com/ml-pipeline/release/$SDK_VERSION/kfp.tar.gz --upgrade
```

### Configure port forwarding to Kubeflow Pipelines service 
If you want to submit Kubeflow Pipelines runs programmatically (rather than through GUI) you need access to `ml-pipeline` service that is running on your GKE cluster. By default the service is not exposed on a public IP intefaces. For the purpose of this tutorial you access the service using port forwarding. Ulternatively, you can expose the service through an external IP.

To configure port forwarding execute the following command in a new Cloud Shell terminal.

```
kubectl port-forward -n kubeflow svc/ml-pipeline 8082:8888
```

The command forwards the local (Cloud Shell) port 8082 to port 8888 (ml-pipeline service port) on the cluster.

Make sure that the terminal window stays open and the command is running when you submit the jobs using KFP SDK client API.


## Rebuilding the components and recompiling the pipelines
Follow the instructions in the README files in `pipelines` and `components` subfolders if you want to rebuild the components and recompile the pipelines.




