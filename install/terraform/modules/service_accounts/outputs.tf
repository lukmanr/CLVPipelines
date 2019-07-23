output "kfp_sa_email" {
    value = google_service_account.kfp_sa.email
}

output "kfp_sa_name" {
    value = google_service_account.kfp_sa.name
}

output "lp_sa_email" {
    value = google_service_account.lp_sa.email
}

output "lp_sa_name" {
    value = google_service_account.lp_sa.name
}

output "kfp_sa_key" {
    value     = google_service_account_key.kfp_sa_key
    sensitive = true
}

