
terraform {
  required_version = ">= 0.12"
}

# Configure GCP provider
provider "google" {
    #credentials = "${file("terraform.json")}"
    project = var.project_id
    region = var.region
    zone = var.zone
}

# Configure service accounts: 
module "service_accounts" {
    source = "./modules/service_accounts"
    kfp_sa_id = var.kfp_sa_id
    lp_sa_id = var.lp_sa_id
}

# Configure GKE cluster
module "kfp_cluster" {
    source = "./modules/kfp_cluster"
    location = var.zone
    cluster_name = var.cluster_name
    sa_email = module.service_accounts.lp_sa_email
    kfp_sa_key = module.service_accounts.kfp_sa_key
}

