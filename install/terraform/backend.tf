terraform {
  backend "gcs" {
    bucket = "jkterraform"
    prefix = "state"
  }
}