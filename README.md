This repository maintains code samples for the tutorial **Operationalizing Customer Lifetime Value model training and deployment with Kubeflow pipelines**. The tutorial is the fifth part of a series that discusses how you can develop and deploy customer lifetime value (CLV) prediction models by using Cloud AI on Google Cloud Platform (GCP).


## Setting up the tutorial's environment
This tutorial uses the following services of Google Cloud Platform:
- Kubeflow Pipelines (KFP) on Google Kubernets Engine (GKE)
- AI Platform Notebooks
- BigQuery
- Dataproc
- Cloud Storage
- AutoML Tables (beta)

Before you begin the environment setup, [enable the corresponding APIs](https://cloud.google.com/apis/docs/enable-disable-apis) for your GCP project.

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
During the tutorial, you use an AI Platform Notebook instance as primary interface. 

### Provision an AI Platform Notebook instance
1. Create a new notebook instance with default options following the [how-to-guide](https://cloud.google.com/ml-engine/docs/notebooks/create-new). Use a **Python** instance type.
2. Follow the instructions in [how-to-guide](https://cloud.google.com/ml-engine/docs/notebooks/create-new) to connect to **JupyterLab** on your notebook instance.
3. Create a new terminal from the **Launcher** tab of **JupyterLab** interface.
4. In the terminal, use **git** to clone the tutorial's github repository.
```
git clone https://github.com/jarokaz/CLVPipelines
```

### Install and configure Kubeflow Pipelines SDK
Before running the tutorial's Jupyter notebooks you need to install Kubeflow Pipelines SDK into the Python 3 kernel of you AI Platform notebook instance and configure access to the Pipelines service on your GKE cluster.

Open a new terminal in **JupyterLab**. Run the following command to install SDK version 0.1.20.
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
kubectl port-forward -n kubeflow svc/ml-pipeline 8081:8888
```

Make sure that the terminal window stays open and the command is running while you walk through the tutorial's notebooks.




## Starting the tutorial
The tutorial's notebooks are located in the `pipelines` folder. Follow the instructions in the notebooks to walk through the tutorial's scenarios.




