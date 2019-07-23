
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

# Configure kubectl and install KFP
resource "null_resource" "configure_kubectl" {
  provisioner "local-exec" {
    command = <<EOT
      gcloud container clusters get-credentials ${module.kfp_cluster.cluster_name} --zone ${var.zone} --project ${var.project_id};
      kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/master/manifests/namespaced-install.yaml
    EOT
  }
}

# Expose an access token for communicating with the GKE cluster.
data "google_client_config" "client" {}

# Configure the Terraform Kubernetes provider with access to the GKE cluster
provider "kubernetes" {
  load_config_file       = false
  host                   = data.template_file.gke_host_endpoint.rendered
  token                  = data.template_file.access_token.rendered
  cluster_ca_certificate = data.template_file.cluster_ca_certificate.rendered
}

# Store KFP SA credentials as user-gcp-sa secret 
resource "kubernetes_secret" "user-gcp-sa" {
   metadata {
       name = "user-gcp-sa"
       namespace = "kubeflow"
   }

   data = {
       "user-gcp-sa.json" = module.service_accounts.kfp_sa_private_key
   }

   depends_on = [null_resource.configure_kubectl]
}



# ---------------------------------------------------------------------------------------------------------------------
# WORKAROUNDS
# ---------------------------------------------------------------------------------------------------------------------

# This is a workaround for the Kubernetes provider to enable passing of module
# outputs to the provider.
data "template_file" "gke_host_endpoint" {
  template = module.kfp_cluster.cluster_endpoint
}

data "template_file" "access_token" {
  template = data.google_client_config.client.access_token
}

data "template_file" "cluster_ca_certificate" {
  template = module.kfp_cluster.cluster_ca_certificate
}
