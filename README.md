This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value model training and deployment with Kubeflow pipelines**. The tutorial is the fifth part of a series that discusses how you can develop and deploy customer lifetime value (CLV) prediction models by using AI Platform on Google Cloud Platform (GCP).


## Setting up the tutorial's environment
This tutorial uses the following services of Google Cloud Platform:
- Kubeflow Pipelines (KFP) on Google Kubernets Engine (GKE)
- AI Platform Notebooks
- BigQuery
- Dataproc
- Cloud Storage
- AutoML Tables (beta)

Before you begin the environment setup [enable the corresponding APIs](https://cloud.google.com/apis/docs/enable-disable-apis) for your GCP project.

## Configuring Kubeflow Pipelines
Use [Cloud Shell](https://cloud.google.com/shell/) to install and configure Kubeflow Pipelines on GKE.

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

### Install Kubeflow pipelines
Install version 1.20 of KFP.
```
PIPELINE_VERSION=4eeeb6e22432ece32c7d0efbd8307c15bfa9b6d3
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$PIPELINE_VERSION/manifests/namespaced-install.yaml
```
### Connect to Kubeflow Pipelines UI

To connect to KFP UI use Cloud Shell to forward a port to KFP UI service. 
```
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
After port forwarding has been established, use Cloud Shell web preview to open KFP UI on port 8080.


## Configuring AI Platform Notebook
During the tutorial, you use an AI Platform Notebook and Kubeflow Pipelines UI as primary interfaces.
To provision an AI Platform Notebook and configure the tutorial's sample code follow the below steps:

1. Create a new notebook instance with default options following the [how-to-guide](https://cloud.google.com/ml-engine/docs/notebooks/create-new). Use a **Python** instance type.
2. Follow the instructions in [how-to-guide](https://cloud.google.com/ml-engine/docs/notebooks/create-new) to connect to **JupyterLab** on your notebook instance.
3. Create a new terminal from the **Launcher** tab of **JupyterLab** interface.
4. In the terminal, use **git** to clone the tutorial's github repository.
```
git clone https://github.com/jarokaz/CLVPipelines
```






