## Provisioning the infrastructure

The provisioning of the insfrastructure required to run the guide's pipelines has been automated with Terraform. The Terraform configuration in the `/terraform/` folder includes the provisioning and configuration of the following infrastructure components:
- GKE cluster
- Kubeflow Pipelines
- Service Accounts used by GKE and KFP
- Container Registry
- Cloud Storage for the pipelines artifacts and sample datasets

To provision the infrastructure:

1. Select or create a GCP project
1. Make sure that the following Cloud APIs are enabled:
   - Compute Engine
   - Cloud Storage
   - Container Registry
   - Kubernetes Engine
   - BigQuery
   - AutoML 
   - Cloud Build
   - Cloud Resource Manager
1. You can enable the services using **GCP Console** or by executing the `enable_apis.sh` script in the `/install` folder.
1. Open a new session in **Cloud Shell**
1. Create a working directory and clone this repo.
1. Start the installation process by executing the following commands:
```
chmod 755 install.sh
./install.sh [PROJECT_ID] [CLUSTER_NAME] [ZONE] [KFP_SA] master
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


Alterantively, you can use the Terraform configuration to perform the same steps. The support for Terraform is experimental. The Terraform configuration is in `./terraform` folder. To provision the environment using Terraform:
1. Clone this repo.
1. Configure the Terraform backend by substituting `bucket` and `state` parameters in the `backend.tf` file with your values.
1. Subsitute the variables in the `terraform.tfvars` file with your values.
    1. `project_id` - your project ID
    1. `cluster_name` - the name of the GKE cluster
    1. `kfp_sa_id` - the name of the Service Account to be used by Kubeflow Pipelines
    1. `lp_sa_id` - the name of the Service Account with least privilages to be used by GKE
    1. `bucket_name` - the GCS bucket to be used for storing artifacts
1. In Cloud Shell:
```
terraform init
terraform apply
```


