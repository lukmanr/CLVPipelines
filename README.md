This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value model training and deployment with Kubeflow pipelines**. The tutorial is the fifth part of a series that discusses how you can develop and deploy customer lifetime value (CLV) prediction models by using AI Platform on Google Cloud Platform (GCP).


## Setting up the tutorial's environment
This tutorial uses the following services of Google Cloud Platform:
- Google Kubernets Engine (GKE)
- AI Platform Notebooks
- BigQuery
- Dataproc
- Cloud Storage
- AutoML Tables (beta)

Before you begin the environment setup [enable the corresponding APIs](https://cloud.google.com/apis/docs/enable-disable-apis) for your GCP project.

## Creating AI Platform Notebook
Create a new notebook instance with default options following the [how-to-guide](https://cloud.google.com/ml-engine/docs/notebooks/create-new). Use a **Python** instance type.

## Creating Compute Engine Instance
```
export IMAGE_FAMILY=common-cpu
export ZONE=[your region]
export INSTANCE_NAME=[your instance name]

gcloud compute instances create $INSTANCE_NAME \
  --zone=$ZONE \
  --image-family=$IMAGE_FAMILY \
  --image-project=deeplearning-platform-release
```

## Connecting to Jupyter Lab
```
gcloud compute ssh $INSTANCE_NAME --zone $ZONE -- -L 8080:localhost:8080
```

## Installing Google Kubernetes Engine (GKE)
Using [Cloud Shell](https://cloud.google.com/shell/), create a single-zone **Standard** cluster .
Make sure to replace the placeholders with your zone and cluster name.
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


## Install Kubeflow pipelines

```
PIPELINE_VERSION=4eeeb6e22432ece32c7d0efbd8307c15bfa9b6d3
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$PIPELINE_VERSION/manifests/namespaced-install.yaml
```


