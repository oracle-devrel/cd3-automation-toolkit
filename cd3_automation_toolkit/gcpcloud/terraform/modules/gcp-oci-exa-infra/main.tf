# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
## Resource Block - Oracle ExaInfra @GCP
## Create Oracle ExaInfra @GCP
##########################################

resource "google_oracle_database_cloud_exadata_infrastructure" "exadata_infrastructure" {
  cloud_exadata_infrastructure_id = var.infra_config.cloud_exadata_infrastructure_id
  display_name                    = var.infra_config.display_name

  location        = var.infra_config.location
  gcp_oracle_zone = var.infra_config.gcp_oracle_zone
  project         = var.infra_config.project

  properties {
    shape         = var.infra_config.shape
    compute_count = var.infra_config.compute_count
    storage_count = var.infra_config.storage_count
    customer_contacts {
      email = var.infra_config.email
    }
    maintenance_window {
      custom_action_timeout_mins       = var.infra_config.maintenance_window.custom_action_timeout_mins
      days_of_week                     = var.infra_config.maintenance_window.days_of_week
      hours_of_day                     = var.infra_config.maintenance_window.hours_of_day
      is_custom_action_timeout_enabled = var.infra_config.maintenance_window.is_custom_action_timeout_enabled
      lead_time_week                   = var.infra_config.maintenance_window.lead_time_week
      months                           = var.infra_config.maintenance_window.months
      patching_mode                    = var.infra_config.maintenance_window.patching_mode
      preference                       = var.infra_config.maintenance_window.preference
      weeks_of_month                   = var.infra_config.maintenance_window.weeks_of_month
    }
    total_storage_size_gb = var.infra_config.total_storage_size_gb
  }
  labels = var.labels


  #deletion_protection = "true"
  lifecycle {
    ignore_changes = [
      properties[0].compute_count,
      properties[0].storage_count
    ]
  }
}


#data "google_oracle_database_db_servers" "exadata_infrastructure" {
#  location                     = "us-central1"
#  project                      = "xxxxxxxxxxxx" # Replace with your Google Cloud Project
#  cloud_exadata_infrastructure = google_oracle_database_cloud_exadata_infrastructure.exadata_infrastructure.cloud_exadata_infrastructure_id
#  depends_on                   = [google_oracle_database_cloud_exadata_infrastructure.exadata_infrastructure]
#}
