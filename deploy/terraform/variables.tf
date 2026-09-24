variable "project_id" {
  description = "The Google Cloud Project ID"
  type        = string
  default     = "quantcube-maritime-prod"
}

variable "region" {
  description = "The default GCP region for serverless compute and BigQuery"
  type        = string
  default     = "europe-west1" # Low latency to Paris HQ / Middle East
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "production"
}

variable "report_generation_schedule" {
  description = "Cron expression for automated daily macro newsletter publication"
  type        = string
  default     = "0 6 * * *" # 06:00 UTC daily
}
