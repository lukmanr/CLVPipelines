variable "region" {
    description = "The region to host the solution's components"
}

variable "zone" {
    description = "The zone to host solutions's components"
}

variable "project_id" {
    description = "The project ID to host the configuration's services"
}

variable "cluster_name" {
    description = "The name of the Kubernetes cluster"
}

variable "kfp_sa_id" {
    description = "The ID of the KFP service account"
}

variable "lp_sa_id" {
    description = "The ID of the Least Priviledge GKE service account"
}

variable "bucket_name" {
    description = "The name of a GCS storage bucket to create in the configuration"
}
