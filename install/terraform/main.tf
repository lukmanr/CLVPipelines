
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
    source = "./modules/gke_cluster"
    location = var.zone
    cluster_name = var.cluster_name
    sa_email = module.service_accounts.lp_sa_email
}


# Configure kubectl, install KFP, and create user-gcp-sa secret
resource "null_resource" "kubectl" {
  provisioner "local-exec" {
    command = <<EOT
      gcloud container clusters get-credentials ${module.kfp_cluster.cluster_name} --zone ${var.zone} --project ${var.project_id};
      kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/master/manifests/namespaced-install.yaml;
      kubectl create secret -n kubeflow generic user-gcp-sa --from-literal=user-gcp-sa.json='${base64decode(module.service_accounts.kfp_sa_private_key)}'
    EOT
  }
}

      


