

data "google_project" "project" {}
data "google_client_config" "default" {}


# Create a GKE cluster with a default node pool and install KFP
resource "google_container_cluster" "kfp_cluster" {
  name               = var.cluster_name
  location           = var.location
  description        = var.description

  initial_node_count = var.node_count

  node_config {
    machine_type = "n1-standard-1"

    metadata = {
      disable-legacy-endpoints = "true"
    }

    service_account = var.sa_email

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }

  provisioner "local-exec" {
    command = <<EOT
      gcloud container clusters get-credentials "${var.cluster_name}" --zone "${var.location}" --project "${data.google_project.project.project_id}"
      export PIPELINE_VERSION="${var.kfp_version}"
      kubectl apply -f https://raw.githubusercontent.com/kubeflow/pipelines/$PIPELINE_VERSION/manifests/kustomize/namespaced-install.yaml
    EOT
  }
}

# Store KFP SA private key as user-gcp-sa secret
provider "kubernetes" {
    load_config_file       = false
    host                   = "https://${google_container_cluster.kfp_cluster.endpoint}"
    token                  = "${data.google_client_config.default.access_token}"
    cluster_ca_certificate = "${base64decode(google_container_cluster.kfp_cluster.master_auth.0.cluster_ca_certificate)}"
}
 
resource "kubernetes_secret" "user-gcp-sa" {
   metadata {
       name = "user-gcp-sa"
       namespace = "kubeflow"
   }

   data = {
       "user-gcp-sa.json" = "${base64decode(var.kfp_sa_key.private_key)}"
   }
}

