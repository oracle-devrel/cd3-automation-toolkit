# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
##########################################
## Resource Block - Oracle ExaInfra @AWS
## Create Oracle ExaInfra @AWS
##########################################


resource "aws_odb_cloud_exadata_infrastructure" "exadata_infrastructure" {
  # Required Arguments
  display_name         = var.infra_config.display_name
  shape                = var.infra_config.shape
  compute_count        = var.infra_config.compute_count
  storage_count        = var.infra_config.storage_count
  availability_zone_id = var.infra_config.availability_zone_id
  region               = var.infra_config.region
  availability_zone    = var.infra_config.availability_zone
  database_server_type = var.infra_config.database_server_type
  storage_server_type  = var.infra_config.storage_server_type

  # Maintenance Window
  maintenance_window {
    patching_mode                    = var.infra_config.maintenance_window.patching_mode
    preference                       = var.infra_config.maintenance_window.preference
    is_custom_action_timeout_enabled = var.infra_config.maintenance_window.is_custom_action_timeout_enabled
    custom_action_timeout_in_mins    = var.infra_config.maintenance_window.custom_action_timeout_in_mins
    lead_time_in_weeks               = var.infra_config.maintenance_window.lead_time_in_weeks
    hours_of_day                     = var.infra_config.maintenance_window.hours_of_day
    weeks_of_month                   = var.infra_config.maintenance_window.weeks_of_month

    # Days of Week
    dynamic "days_of_week" {
      for_each = var.infra_config.maintenance_window.days_of_week != null ? var.infra_config.maintenance_window.days_of_week : []
      content {
        name = days_of_week.value
      }
    }

    # Months
    dynamic "months" {
      for_each = var.infra_config.maintenance_window.months != null ? var.infra_config.maintenance_window.months : []
      content {
        name = months.value
      }
    }
  }

  # Customer Contacts
  dynamic "customer_contacts_to_send_to_oci" {
    for_each = var.infra_config.customer_contacts
    content {
      email = customer_contacts_to_send_to_oci.value.email
    }
  }

  # Tags
  tags = var.tags
}

# Post-creation data lookup
data "aws_odb_db_servers" "exadata_infrastructure" {
  cloud_exadata_infrastructure_id = aws_odb_cloud_exadata_infrastructure.exadata_infrastructure.id
  depends_on                      = [aws_odb_cloud_exadata_infrastructure.exadata_infrastructure]
}

