output "cluster_name" {
    value = google_container_cluster.kfp_cluster.name
}

output "cluster_endpoint" {
    value = google_container_cluster.kfp_cluster.endpoint
}


# The following outputs allow authentication and connectivity to the GKE Cluster.
output "client_certificate" {
  description = "Public certificate used by clients to authenticate to the cluster endpoint."
  value       = base64decode(google_container_cluster.kfp_cluster.master_auth[0].client_certificate)
}

output "client_key" {
  description = "Private key used by clients to authenticate to the cluster endpoint."
  value       = base64decode(google_container_cluster.kfp_cluster.master_auth[0].client_key)
}

output "cluster_ca_certificate" {
  description = "The public certificate that is the root of trust for the cluster."
  value       = base64decode(google_container_cluster.kfp_cluster.master_auth[0].cluster_ca_certificate)
}