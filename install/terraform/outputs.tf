output "cluster_name" {
    value = module.kfp_cluster.cluster_name
}

output "cluster_endpoint" {
    value = module.kfp_cluster.cluster_endpoint
}


output "kfp_sa_email" {
    value = module.service_accounts.kfp_sa_email
}

output "kfp_sa_name" {
    value = module.service_accounts.kfp_sa_name
}

output "lp_sa_email" {
    value = module.service_accounts.lp_sa_email
}

output "lp_sa_name" {
    value = module.service_accounts.lp_sa_name
}

output "client_key" {
  description = "Private key used by clients to authenticate to the cluster endpoint."
  value       = module.kfp_cluster.client_key
}