# Predicting Customer Lifetime Value with Kubeflow Pipelines

## Solution Overview

This repository maintains the source code for  **Predicting Customer Lifetime Value with Kubeflow Pipelines** solution.

The **Predicting Customer Lifetime Value** solution  delivers automation of Customer Lifetime Value (CLV) modeling techniques described in the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series of articles.

The below diagram depicts the high level architecture of the solution:

![KFP Runtime](/images/architecture.jpg)

The solution utilizes an architectural pattern where Kubeflow Pipelines is used solely as an orchestrator of . The primary goal of the pipelines in the solution is to orchestrate **BigQuery** and **AutoML Tables** services. **BigQuery** is used for data pr


The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running on Google Cloud Platform. The solution's pipelines access **Cloud Storage**, **BigQuery**, and **AutoML Tables** services through a set of Kubeflow Pipelines components that wrap the respective **Google Cloud APIs**.The container images for the components utilized by the pipelines are managed in **Container Registry**.

The 


## Installing Kubeflow Pipelines

The solution accelerator has been developed and tested on Kubeflow Pipelines on Google Cloud Platform Kubernetes Engine (GKE). 

The runtime environment required by the solution accelerator is depicted on the below diagram:




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

