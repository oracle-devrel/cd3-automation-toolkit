# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#

data "azurerm_virtual_network" "virtual_network" {
  depends_on          = [module.avm_network]
  for_each            = var.az_oci_adb != null ? var.az_oci_adb : {}
  name                = each.value.virtual_network_name
  resource_group_name = each.value.network_resource_group_name
}

data "azurerm_subnet" "subnet" {
  depends_on           = [module.avm_network]
  for_each             = var.az_oci_adb != null ? var.az_oci_adb : {}
  name                 = each.value.delegated_subnet_name
  virtual_network_name = each.value.virtual_network_name
  resource_group_name  = each.value.network_resource_group_name
}


#############################
# Module Block - ADB @Azure
# Create ADB
#############################

module "adb-azure" {
  for_each = var.az_oci_adb != null ? var.az_oci_adb : {}

  # depends_on = [ module.azure-resource-grp ]
  source = "./modules/azurerm-oci-adb"
  name   = each.value.display_name
  #resource_group_name              = data.azurerm_resource_group.resource_group[each.key].id
  virtual_network_id               = data.azurerm_virtual_network.virtual_network[each.key].id
  subnet_id                        = data.azurerm_subnet.subnet[each.key].id
  resource_group_name              = each.value.resource_group_name
  location                         = each.value.az_region
  display_name                     = each.value.display_name
  db_workload                      = each.value.db_workload
  mtls_connection_required         = each.value.mtls_connection_required
  backup_retention_period_in_days  = each.value.backup_retention_period_in_days
  compute_model                    = each.value.compute_model
  data_storage_size_in_tbs         = each.value.data_storage_size_in_tbs
  auto_scaling_for_storage_enabled = each.value.auto_scaling_for_storage_enabled

  admin_password       = each.value.admin_password
  auto_scaling_enabled = each.value.auto_scaling_enabled
  character_set        = each.value.character_set
  compute_count        = each.value.compute_count
  ncharacter_set       = each.value.ncharacter_set
  license_model        = each.value.license_model
  db_version           = each.value.db_version
  customer_contacts    = each.value.customer_contacts
  tags                 = each.value.common_tags
}
