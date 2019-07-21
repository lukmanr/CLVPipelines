# Configure the KFP service account

resource "google_service_account" "kfp_sa" {
    account_id = var.kfp_sa_id
    display_name = "KFP Service Account"
}

resource "google_project_iam_member" "service_account-storage_admin" {
  project = google_service_account.kfp_sa.project
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.kfp_sa.email}"
}

resource "google_project_iam_member" "service_account-bigquery_admin" {
  project = google_service_account.kfp_sa.project
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.kfp_sa.email}"
}

resource "google_project_iam_member" "service_account-automl_admin" {
  project = google_service_account.kfp_sa.project
  role    = "roles/automl.admin"
  member  = "serviceAccount:${google_service_account.kfp_sa.email}"
}

resource "google_project_iam_member" "service_account-automl_predictor" {
  project = google_service_account.kfp_sa.project
  role    = "roles/automl.predictor"
  member  = "serviceAccount:${google_service_account.kfp_sa.email}"
}

resource "google_service_account_key" "kfp_sa_key" {
    service_account_id = "${google_service_account.kfp_sa.name}"
}

# Configure the Least Priviledge service account with the minimum necessary roles and permissions in order to run the GKE cluster

resource "google_service_account" "lp_sa" {
    account_id = var.lp_sa_id
    display_name = "Least Priviledge Service Account"
}

resource "google_project_iam_member" "service_account-log_writer" {
  project = google_service_account.lp_sa.project
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.lp_sa.email}"
}

resource "google_project_iam_member" "service_account-metric_writer" {
  project = google_service_account.lp_sa.project
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.lp_sa.email}"
}

resource "google_project_iam_member" "service_account-monitoring_viewer" {
  project = google_service_account.lp_sa.project
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.lp_sa.email}"
}

resource "google_project_iam_member" "service_account-resource-metadata-writer" {
  project = google_service_account.lp_sa.project
  role    = "roles/stackdriver.resourceMetadata.writer"
  member  = "serviceAccount:${google_service_account.lp_sa.email}"
}