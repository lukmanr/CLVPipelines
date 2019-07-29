variable "project_id" {
    description = "The GCP project ID"
}

variable "zone" {
    description = "The zone of the GKE cluster"
}

variable "cluster_name" {
    description = "The name of the Kubernetes cluster"
}

variable "kfp_sa_id" {
    description = "The ID of the Kubeflow Pipelines service account"
}

variable "lp_sa_id" {
    description = "The ID of the Least Priviledge GKE service account"
}

variable "bucket_name" {
    description = "The name of a GCS storage bucket that will be used as an artifact store"
}
