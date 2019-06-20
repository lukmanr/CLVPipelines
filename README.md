# Predicting Customer Lifetime Value with Kubeflow Pipelines

## Solution Overview

This repository maintains the source code for  **Predicting Customer Lifetime Value with Kubeflow Pipelines** solution.

The **Predicting Customer Lifetime Value** solution  delivers automation of Customer Lifetime Value (CLV) modeling techniques described in the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series of articles.

The primary goal of the solution is to orchestrate two Machine Learning workflows:
- The training and deployment of the Customer Lifetime Value predictive model.
- The batch inference using the deployed Customer Lifetime Value predictive model.

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
where
Parameter | Description
----------|------------
PROJECT_ID|Project ID of the GCP project you selected for the solution
CLUSTER_NAME| The name of the GKE cluster to create. If the cluster with that name already exists the script will skip the creation step. 
ZONE | The zone for the cluster. Since AutoML only support` us-central1` it is recommended to create the cluster in one of the zones in the same region
KFP_SA | The name of the service account to be used by Kubeflow Pipelines. If the service account with that name already exists the account is reused.
KFP_VERSION | The version of Kubeflow Pipelines to install. It is recommended to use the latest version from the master branch in Kubeflow Pipelines GitHub repo.



  

### Building runtime environment

The lightweight deployment of Kubeflow Pipelines on GKE has been automated with a bash script. You can find the script in the `/kubeflow_pipelines_setup` folder.

The solution accelerator has been developed using Kubeflow v5.0 and Kubeflow Pipelines v0.1.20


### Training and inference KFP pipelines

The solution accelerator includes two template KFP Pipelines:
- The pipeline that automates CLV model training and deployment
- The pipeline that automates batch inference using a trained CLV model

Both pipelines use BigQuery for data preprocessing and feature engineering and AutoML Tables for model training, deployment and inference.

Refer to `/clv_pipelines/README.md` for more information on the pipelines' design and usage.

### AutoML Tables KFP components

The pipelines utilize a number of KFP components including custom KFP components that wrap selected AutoML Tables APIs. The source code for the components can be found in the `components/automl_tables` folder.

Refer to `/automl_tables_components/README.md` for more information on the components' design and usage.

### Build and deployment automation

The process of customizing, compiling and deploying the pipelines and the AutoML Tables components has been automated using Google Cloud Build service. The automation script and its documentation are in the `/build-deploy` folder.

### Sample integration code

The pipelines can be run using Kubeflow Pipelines UI but they can also be integrated with other systems by using `kfp.Client()` programmatic interface. The `/run` folder contains codes samples demonstrating how to use `kfp.Client()` interface.





## Acknowledgements

The sample dataset used in the solution accelrator is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. 




The solution accelerater includes the following components:
- Training and inference Kubeflow Pipelines (KFP) pipelines - `/pipelines`
- AutoML Tables KFP components - `/components`
- Cloud Build configuration for automated building and deployment of the solution's KFP components and pipelines - `/deploy`
- Sample integration code demonstrating  - `/run`

