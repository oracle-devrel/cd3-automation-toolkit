# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Resource Block - Oracle ExaInfra @Azure
## Create Oracle ExaInfra @Azure
#####################################

resource "azurerm_oracle_exadata_infrastructure" "exadata_infrastructure" {
  # Required
  resource_group_name = var.resource_group_name
  location            = var.location
  zones               = [var.zone]

  name                = var.name
  display_name        = var.name

  shape         = var.shape
  compute_count = var.compute_count
  storage_count = var.storage_count

  #database_server_type = var.database_server_type
  #storage_server_type  = var.storage_server_type

  # Optional
  customer_contacts  = var.customer_contacts
  tags               = var.tags

  maintenance_window {
      patching_mode = var.maintenance_window.patching_mode
      preference = var.maintenance_window.preference
      lead_time_in_weeks = coalesce(var.maintenance_window.lead_time_in_weeks,1)
      months = coalesce(var.maintenance_window.months,[])
      weeks_of_month = coalesce(var.maintenance_window.weeks_of_month,[])
      days_of_week = coalesce(var.maintenance_window.days_of_week,[])
      hours_of_day = coalesce(var.maintenance_window.hours_of_day,[])
  }

  lifecycle {
    ignore_changes = [
      # Updatable from OCI
      compute_count,
      storage_count,
      database_server_type,
      storage_server_type,
      customer_contacts,
      maintenance_window
    ]
  }
}

data "azurerm_oracle_exadata_infrastructure" "exadata_infrastructures" {
  name                = var.name
  resource_group_name = var.resource_group_name
  depends_on = [azurerm_oracle_exadata_infrastructure.exadata_infrastructure]
}