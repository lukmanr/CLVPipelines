variable "region" {
    description = "The region to host the solution's components"
    default = "us-central1"
}

variable "zone" {
    description = "The zone to host solutions's components"
    default = "us-central1-a"
}

variable "project_id" {
    description = "The project ID to host the solution components"
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
