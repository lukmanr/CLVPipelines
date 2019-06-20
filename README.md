# Predicting Customer Lifetime Value with Kubeflow Pipelines

## Solution Overview

This repository maintains the source code for the **Predicting Customer Lifetime Value with Kubeflow Pipelines** solution.

The **Predicting Customer Lifetime Value** solution  delivers automation of Customer Lifetime Value (CLV) modeling techniques described in the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series of articles.

The primary goal of the solution is to orchestrate two Machine Learning workflows:
- The training and deployment of the Customer Lifetime Value predictive model.
- Batch inference using the deployed Customer Lifetime Value predictive model.

The below diagram depicts the high level architecture of the solution:

![KFP Runtime](/images/architecture.jpg)

In the solution, **Kubeflow Pipelines** is used solely as an orchestrator of Google Cloud  managed services: **BigQuery**, **AutoML Tables**, and **Cloud Storage**. **BigQuery** is used for data pre-processing and feature engineering. **AutoML Tables** is used for model training and inference. **Cloud Storage** is used primarly for staging input and output data. 

The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running on Google Cloud Platform. The solution's training and inference pipelines access **BigQuery**,  **AutoML Tables** services through a set of Kubeflow Pipelines components that wrap the respective **Google Cloud APIs**. The container images for the components utilized by the pipelines are managed in **Container Registry**.



## Installing Kubeflow Pipelines

The solution has been developed and tested on Kubeflow Pipelines on Google Cloud Platform Kubernetes Engine (GKE). 

You can run the solution on a full **Kubeflow** installation  or on a lightweight deployment that only includes core Kubeflow Pipelines services. The full Kubeflow installation can be provisioned following [the Kubeflow on GCP guide](https://www.kubeflow.org/docs/gke/deploy/). The lightweight Kubeflow Pipelines deployment can be performed using the automation script delivered as a part of the solution.

To provision the lightweight Kubeflow Pipelines deployment:
1. Select or create a GCP project
1. Make sure that the following Cloud APIs are enabled:
   - Compute Engine
   - Cloud Storage
   - Container Registry
   - Kubernetes Engine
   - BigQuery
   - AutoML 
   - Cloud Build
1. Open a new session in **Cloud Shell**
1. Create a working directory and copy to it the `install.sh` script from the `/install` folder of this repo.
1. Start the installation process by executing the following commands:
```
chmod 755 install.sh
./install.sh [PROJECT_ID] [CLUSTER_NAME] [REGION] [KFP_SA] master
```

Parameter | Description
----------|------------
PROJECT_ID|Project ID of the GCP project you selected for the solution
CLUSTER_NAME| The name of the GKE cluster to create. If the cluster with that name already exists the script will skip the creation step. 
ZONE | The zone for the cluster. Since AutoML only support` us-central1` it is recommended to create the cluster in one of the zones in the same region
KFP_SA | The name of the service account to be used by Kubeflow Pipelines. If the service account with that name already exists the account is reused.
KFP_VERSION | The version of Kubeflow Pipelines to install. It is recommended to use the latest version from the master branch in Kubeflow Pipelines GitHub repo.

The installation script goes through the following steps.

1. Creates a single-zone, Standard Google Kubernetes Cluster. The nodes in the cluster are configured with the cloud-platform instance scope, which gives the nodes access to all Cloud APIs including BigQuery, Cloud Storage, and AutoML Tables utilized in the solution. All other properties of the cluster are set to defaults.
1. Installs Kubeflow Pipelines into the  `kubeflow` namespace.
1. Creates a service account to be used by KFP
1. Creates a private key for the service account.
1. Stores the key as the user-gcp-sa Kubernetes secret in the kubeflow namespace.
1. Assigns the service account permissions in for BigQuery, Cloud Storage and AutoML Tables.

## Building and deploying the solution

The solution includes KFP pipelines and KFP components. Before the pipelines can be run they have to be compiled and the solution's components need to be packaged in container images. The building and deploying of the solution has been automated using **Cloud Build**. Refer to [README](/deploy/README.md) in the `/deploy` folder of this repo for the detailed deployment instructions.


## Repository structure

`/pipelines`
The source code for two template KFP Pipelines:
- The pipeline that automates CLV model training and deployment
- The pipeline that automates batch inference 


`/components`

The source code for the KFP components that wrap selected **AutoML Tables** APIs.

Refer to `/automl_tables_components/README.md` for more information on the components' design and usage.

`/install`

Lightweight Kubeflow Pipelines deployment installation script

`/deploy`

Cloud Build configuration for automated building and deployment of the solution.

`/run`

Sample code demonstrating how to use the `kfp.Client()` programmatic interface to KFP services.



## Acknowledgements

The sample dataset used in the solution accelrator is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. 



