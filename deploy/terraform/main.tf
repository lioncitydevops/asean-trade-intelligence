terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# 1. Enable Core GCP APIs
resource "google_project_service" "services" {
  for_each = toset([
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com",
    "cloudscheduler.googleapis.com",
    "aiplatform.googleapis.com",
  ])
  service            = each.key
  disable_on_destroy = false
}

# 2. Cloud Storage Buckets
resource "google_storage_bucket" "reports_bucket" {
  name          = "${var.project_id}-published-reports"
  location      = var.region
  force_destroy = false

  uniform_bucket_level_access = true

  lifecycle_rule {
    action {
      type = "SetStorageClass"
      storage_class = "NEARLINE"
    }
    condition {
      age = 90
    }
  }
}

resource "google_storage_bucket" "raw_lakehouse_bucket" {
  name          = "${var.project_id}-maritime-lakehouse"
  location      = var.region
  force_destroy = false
  uniform_bucket_level_access = true
}

# 3. Google Cloud Pub/Sub Telemetry Ingestion Topics
resource "google_pubsub_topic" "ais_raw_topic" {
  name = "ais-telemetry-raw"
  labels = {
    env = var.environment
  }
}

resource "google_pubsub_topic" "market_prices_topic" {
  name = "market-prices"
}

# 4. BigQuery Spatial Dataset & Tables
resource "google_bigquery_dataset" "maritime_dataset" {
  dataset_id                  = "quantcube_maritime"
  friendly_name               = "QuantCube Maritime Telemetry Lakehouse"
  description                 = "Partitioned BigQuery GIS dataset for global tanker tracking and baseline models"
  location                    = var.region
  default_table_expiration_ms = null
}

# 5. Cloud Run Service: Interactive Real-Time Terminal & API
resource "google_cloud_run_v2_service" "terminal_api" {
  name     = "quantcube-maritime-terminal"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    containers {
      image = "gcr.io/${var.project_id}/maritime-terminal:latest"
      
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "REPORTS_BUCKET"
        value = google_storage_bucket.reports_bucket.name
      }
    }
  }

  depends_on = [google_project_service.services]
}

# 6. Allow Unauthenticated Public Access for the Terminal
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.terminal_api.location
  service  = google_cloud_run_v2_service.terminal_api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 7. Cloud Scheduler: Automated Daily Report Generation Trigger (06:00 UTC)
resource "google_cloud_scheduler_job" "daily_report_job" {
  name        = "daily-macro-report-publisher"
  description = "Triggers daily automated QuantCube Macro Insights research newsletter compilation"
  schedule    = var.report_generation_schedule
  time_zone   = "UTC"

  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_v2_service.terminal_api.uri}/api/generate-report"
    
    headers = {
      "Content-Type" = "application/json"
    }
  }
}
