# Beacon Studio Infrastructure
# Terraform configuration for GCP resources

terraform {
  required_version = ">= 1.5"
  
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  
  backend "gcs" {
    bucket = "beacon-terraform-state"
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "beacon_db" {
  name             = "beacon-db-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  
  settings {
    tier              = "db-custom-2-7680" # 2 vCPU, 7.68 GB RAM
    availability_type = "REGIONAL" # High availability
    
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
      }
    }
    
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.beacon_vpc.id
      require_ssl     = true
    }
    
    database_flags {
      name  = "max_connections"
      value = "100"
    }
  }
  
  deletion_protection = true
}

resource "google_sql_database" "beacon_database" {
  name     = "beacon_studio"
  instance = google_sql_database_instance.beacon_db.name
}

resource "google_sql_user" "beacon_user" {
  name     = "beacon_app"
  instance = google_sql_database_instance.beacon_db.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Cloud Storage Bucket for Files
resource "google_storage_bucket" "beacon_files" {
  name          = "beacon-prod-files-${var.project_id}"
  location      = var.region
  force_destroy = false
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    condition {
      age = 90
      matches_prefix = ["exports/"]
    }
    action {
      type = "Delete"
    }
  }
  
  cors {
    origin          = ["https://shlinx.com"]
    method          = ["GET", "POST", "PUT", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }
}

# VPC Network
resource "google_compute_network" "beacon_vpc" {
  name                    = "beacon-vpc-${var.environment}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "beacon_subnet" {
  name          = "beacon-subnet-${var.region}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.beacon_vpc.id
}

# VPC Connector for Cloud Run to access Cloud SQL
resource "google_vpc_access_connector" "connector" {
  name          = "beacon-vpc-connector"
  region        = var.region
  network       = google_compute_network.beacon_vpc.name
  ip_cidr_range = "10.8.0.0/28"
}

# Cloud Scheduler Jobs
resource "google_cloud_scheduler_job" "storage_reconciliation" {
  name             = "beacon-storage-reconciliation"
  description      = "Daily storage reconciliation job"
  schedule         = "0 3 * * *" # 3 AM daily
  time_zone        = "America/New_York"
  attempt_deadline = "600s"
  
  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.beacon_backend.status[0].url}/admin/storage-reconciliation"
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

resource "google_cloud_scheduler_job" "purge_deleted" {
  name             = "beacon-purge-deleted-workspaces"
  description      = "Daily purge deleted workspaces job"
  schedule         = "0 4 * * *" # 4 AM daily
  time_zone        = "America/New_York"
  attempt_deadline = "600s"
  
  http_target {
    http_method = "POST"
    uri         = "${google_cloud_run_service.beacon_backend.status[0].url}/admin/purge-deleted-workspaces"
    
    oidc_token {
      service_account_email = google_service_account.scheduler.email
    }
  }
}

# Service Accounts
resource "google_service_account" "cloud_run" {
  account_id   = "beacon-cloud-run"
  display_name = "Beacon Cloud Run Service Account"
}

resource "google_service_account" "scheduler" {
  account_id   = "beacon-scheduler"
  display_name = "Beacon Cloud Scheduler Service Account"
}

# IAM Roles
resource "google_project_iam_member" "cloud_run_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_storage_bucket_iam_member" "cloud_run_storage" {
  bucket = google_storage_bucket.beacon_files.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_cloud_run_service_iam_member" "scheduler_invoker" {
  service  = google_cloud_run_service.beacon_backend.name
  location = google_cloud_run_service.beacon_backend.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler.email}"
}

# Cloud Run Service (placeholder - usually deployed via Cloud Build)
resource "google_cloud_run_service" "beacon_backend" {
  name     = "beacon-backend"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.cloud_run.email
      
      containers {
        image = "gcr.io/${var.project_id}/beacon-backend:latest"
        
        ports {
          container_port = 8080
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
        
        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }
        
        env {
          name  = "GCS_BUCKET_NAME"
          value = google_storage_bucket.beacon_files.name
        }
        
        env {
          name  = "GCS_PROJECT_ID"
          value = var.project_id
        }
      }
      
      container_concurrency = 80
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "100"
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.connector.name
        "run.googleapis.com/vpc-access-egress"    = "private-ranges-only"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allow unauthenticated access to Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.beacon_backend.name
  location = google_cloud_run_service.beacon_backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "backend_url" {
  value       = google_cloud_run_service.beacon_backend.status[0].url
  description = "Beacon Backend Cloud Run URL"
}

output "database_connection_name" {
  value       = google_sql_database_instance.beacon_db.connection_name
  description = "Cloud SQL Connection Name"
}

output "storage_bucket_name" {
  value       = google_storage_bucket.beacon_files.name
  description = "Cloud Storage Bucket Name"
}

