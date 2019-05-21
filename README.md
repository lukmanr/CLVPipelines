This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value model training and deployment with Kubeflow Pipelines**. The tutorial is the fifth part of the series [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro).
The fifth part focuses on demonstrating how to operationalize model training, deployment, and inference using Kubeflow Pipelines on Google Kubernetes Engine.

The repository includes two subfolders: `pipelines` and `components`.

The `pipelines` folder contains the example pipelines that demonstrate how to utilize pre-built and custom **Kubeflow Pipelines Components** to orchestrate data preparation, model training, model deployment and inference. Refer to README files associated with each pipeline for more details.

The `components` folder contains an example implementation of a custom Kubeflow Pipeline Component. This component is a wrapper around **AutoML Tables API**.

To run the code samples you need to set up a Google Cloud Platform (GCP) project with the following GCP services enabled:
- Google Kubernetes Engine (GKE)
- BigQuery
- Dataproc
- Cloud Storage
- AutoML Tables (beta)

Refer to this [how-to-guide](https://cloud.google.com/apis/docs/enable-disable-apis) to enable the required services.

## Configuring Kubeflow Pipelines
You are going to use [Cloud Shell](https://cloud.google.com/shell/) to install and configure Kubeflow Pipelines on Google Kubernetes Engine.

### Install Google Kubernetes Engine (GKE)
Open a Cloud Shell session and create a single-zone **Standard** cluster. Make sure to replace the placeholders with your zone and cluster name.
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
The code samples have been developed for version 1.20 of KFP.
```
PIPELINE_VERSION=4eeeb6e22432ece32c7d0efbd8307c15bfa9b6d3
kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$PIPELINE_VERSION/manifests/namespaced-install.yaml
```
### Connect to Kubeflow Pipelines UI

To connect to KFP UI use Cloud Shell to forward a port to KFP UI service. 
```
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```
After port forwarding has been established, use Cloud Shell web preview to open KFP UI on port 8080. Note that it may take a couple of minutes before the UI is fully functional.

You are now ready to execute the sample pipelines using Kubeflow Pipelines UI. Refer to the **Tutorial (TBD)** for the walk-through instructions.

## Configuring a development environment

To re-build the KFP components, recompile the pipelines, or use a programmatic inteface to Kubeflow Pipelines, you need a development environment with the following configuration:
- Python 3.5+
- Docker
- Kubeflow Pipelines SDK v 1.20

The following instructions show how to configure Cloud Shell as the development environment. 


### Install and configure Kubeflow Pipelines SDK on Cloud Shell
Docker and Python 3.5.3 are pre-installed in Cloud Shell. The only missing component is KFP SDK.


To install KFP SDK v0.1.20 open a new Cloud Shell session and run the following command:
```
SDK_VERSION=0.1.20
python3 -m pip install https://storage.googleapis.com/ml-pipeline/release/$SDK_VERSION/kfp.tar.gz --upgrade
```

### Configure port forwarding to the Pipeline service 
Get the credentials to your GKE cluster.
```
ZONE=[your zone]
CLUSTERNAME=[your cluster name]
gcloud container clusters get-credentials $CLUSTERNAME --zone $ZONE
```
Configure port forwarding.
```
kubectl port-forward -n kubeflow svc/ml-pipeline 8082:8888
```

Make sure that the terminal window stays open and the command is running while you walk through the tutorial's notebooks.




## Starting the tutorial
The tutorial's notebooks are located in the `pipelines` folder. Follow the instructions in the notebooks to walk through the tutorial's scenarios.




