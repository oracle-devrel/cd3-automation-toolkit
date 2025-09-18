# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
## Resource Block - Oracle ADB @Azure
## Create Oracle ADB @Azure
#####################################

resource "azurerm_oracle_autonomous_database" "autonomous_database" {
  name                             = var.name
  resource_group_name              = var.resource_group_name
  location                         = var.location
  subnet_id                        = var.subnet_id
  display_name                     = var.display_name
  db_workload                      = var.db_workload
  mtls_connection_required         = var.mtls_connection_required
  backup_retention_period_in_days  = var.backup_retention_period_in_days
  compute_model                    = var.compute_model
  data_storage_size_in_tbs         = var.data_storage_size_in_tbs
  auto_scaling_for_storage_enabled = var.auto_scaling_for_storage_enabled
  virtual_network_id               = var.virtual_network_id
  admin_password                   = var.admin_password
  auto_scaling_enabled             = var.auto_scaling_enabled
  character_set                    = var.character_set
  compute_count                    = var.compute_count
  national_character_set           = var.ncharacter_set
  license_model                    = var.license_model
  db_version                       = var.db_version
  customer_contacts                = var.customer_contacts
  tags                             = var.tags
  lifecycle {
    ignore_changes = [
      name,
      display_name,
      db_workload,
      mtls_connection_required,
      #backup_retention_period_in_days,
      compute_model,
      #data_storage_size_in_tbs,
      #auto_scaling_for_storage_enabled,
      #auto_scaling_enabled,
      character_set,
      admin_password,
      # compute_count,
      national_character_set,
      license_model,
      db_version,
      customer_contacts
    ]
  }
}

/*
data "azurerm_oracle_autonomous_database" "this" {
  depends_on = [ azurerm_oracle_autonomous_database.this ]
  name                = azurerm_oracle_autonomous_database.this.name
  resource_group_name = azurerm_oracle_autonomous_database.this.resource_group_name
}
*/