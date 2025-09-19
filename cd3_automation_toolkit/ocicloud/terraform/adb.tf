# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Module Block - Autonomous database
## Create autonomous database
#############################
data "oci_core_subnets" "oci_subnets_adb" {
  # depends_on = [module.subnets] # Uncomment to create Network and FSS together
  #for_each       = var.adb != null ? var.adb : {}
  for_each       = { for k, v in var.adb : k => v if v.vcn_name != null }
  compartment_id = each.value.subnet_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.subnet_compartment_id)) > 0 ? each.value.subnet_compartment_id : var.compartment_ocids[each.value.subnet_compartment_id]) : var.compartment_ocids[each.value.subnet_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = length(regexall("ocid1.vcn.oc*", each.value.vcn_name)) > 0 ? each.value.vcn_name : data.oci_core_vcns.oci_vcns_adb[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_adb" {
  # depends_on = [module.vcns] # Uncomment to create Network and FSS together
  #for_each       = var.adb != null ? var.adb : {}
  for_each       = { for k, v in var.adb : k => v if v.vcn_name != null }
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
  state = "Available"
}
/*output "vcns_data" {
  value = { for k, v in data.oci_core_vcns.oci_vcns_adb : k => v }
}*/
locals {
  # Get all admin_password values from var.adb
  all_passwords = [
    for adb_entry in values(var.adb) : adb_entry.admin_password
  ]

  # Remove empty values
  non_empty_passwords = compact(local.all_passwords)

  # Keep only ones that start with "ocid1.vaultsecret.oc"
  vault_secret_ocids = toset([
    for pw in local.non_empty_passwords : pw
    if length(regexall("ocid1.vaultsecret.oc*", pw)) > 0
  ])
  decoded_vault_passwords = {
    for k, v in data.oci_secrets_secretbundle.vault_secrets :
    k => base64decode(v.secret_bundle_content[0].content)
  }
}
data "oci_secrets_secretbundle" "vault_secrets" {
  for_each  = local.vault_secret_ocids
  secret_id = each.value
}


module "adb" {
  source   = "../../modules/database/adb"
  for_each = var.adb != null ? var.adb : {}
  # depends_on = [module.nsgs]
  #admin_password                                             = each.value.admin_password
  admin_password = (
    length(regexall("ocid1.vaultsecret.oc*", each.value.admin_password)) > 0 ?
    local.decoded_vault_passwords[each.value.admin_password] :
    each.value.admin_password
  )
  compartment_id                                             = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  are_primary_whitelisted_ips_used       = each.value.are_primary_whitelisted_ips_used != null ? each.value.are_primary_whitelisted_ips_used : null
  auto_refresh_frequency_in_seconds      = each.value.auto_refresh_frequency_in_seconds != null ? each.value.auto_refresh_frequency_in_seconds : null
  auto_refresh_point_lag_in_seconds      = each.value.auto_refresh_point_lag_in_seconds != null ? each.value.auto_refresh_point_lag_in_seconds : null
  autonomous_container_database_id                           = each.value.autonomous_container_database_id != null ? each.value.autonomous_container_database_id : null
  adb_source         = each.value.adb_source != null ? each.value.adb_source :null
  source_id = each.value.source_id != null ? each.value.source_id : null
  autonomous_database_source_backup_id                       = each.value.autonomous_database_source_backup_id != null ? each.value.autonomous_database_source_backup_id : null
  autonomous_database_id                              = each.value.autonomous_database_id != null ? each.value.autonomous_database_id : null
  autonomous_maintenance_schedule_type   = each.value.autonomous_maintenance_schedule_type != null ? each.value.autonomous_maintenance_schedule_type : null
  backup_retention_period_in_days        = each.value.backup_retention_period_in_days != null ? each.value.backup_retention_period_in_days : null
  character_set                                              = each.value.character_set
  compute_count                                              = each.value.compute_count
  compute_model                                              = each.value.compute_model
  customer_contacts                                          = each.value.customer_contacts
  data_safe_status                       = each.value.data_safe_status != null ? each.value.data_safe_status : null
  data_storage_size_in_gb                = each.value.data_storage_size_in_gb != null ? each.value.data_storage_size_in_gb : null
  data_storage_size_in_tbs                                   = each.value.data_storage_size_in_tbs != null ? each.value.data_storage_size_in_tbs : null
  database_edition                                           = each.value.database_edition != null ? each.value.database_edition: null
  db_name                                                    = each.value.db_name
  db_version                                                 = each.value.db_version
  db_workload                                                = each.value.db_workload
  defined_tags                                               = each.value.defined_tags
  display_name                                               = each.value.display_name
  kms_key_id                                                 = each.value.kms_key_id != null ? each.value.kms_key_id : null
  vault_id                                                   = each.value.vault_id != null ? each.value.vault_id : null
  freeform_tags                                              = each.value.freeform_tags
  network_compartment_id                                     = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  subnet_id                                                  = each.value.subnet_id != null ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_adb[each.key].subnets.*.id[0]) : null
  vcn_id                                                     = each.value.vcn_name != null ?(length(regexall("ocid1.vcn.oc*", each.value.vcn_name)) > 0 ? each.value.vcn_name : data.oci_core_vcns.oci_vcns_adb[each.key].virtual_networks.*.id[0]):null
  in_memory_percentage                   = each.value.in_memory_percentage != null ? each.value.in_memory_percentage : null
  is_auto_scaling_enabled                = each.value.is_auto_scaling_enabled != null ? each.value.is_auto_scaling_enabled : null
  is_auto_scaling_for_storage_enabled    = each.value.is_auto_scaling_for_storage_enabled != null ? each.value.is_auto_scaling_for_storage_enabled : null
  is_backup_retention_locked             = each.value.is_backup_retention_locked != null ? each.value.is_backup_retention_locked : null
  is_dedicated                           = each.value.is_dedicated != null ? each.value.is_dedicated : null
  is_local_data_guard_enabled            = each.value.is_local_data_guard_enabled != null ? each.value.is_local_data_guard_enabled : null
  is_mtls_connection_required            = each.value.is_mtls_connection_required != null ? each.value.is_mtls_connection_required : null
  is_replicate_automatic_backups         = each.value.is_replicate_automatic_backups != null ? each.value.is_replicate_automatic_backups : null
  license_model                                              = each.value.license_model != null ? each.value.license_model : null
  ncharacter_set                                             = each.value.ncharacter_set
  network_security_group_ids                                 = each.value.nsg_ids != null ? each.value.nsg_ids : null
  ocpu_count                                              = each.value.ocpu_count != null ? each.value.ocpu_count : null
  private_endpoint_ip                    = each.value.private_endpoint_ip != null ? each.value.private_endpoint_ip : null
  private_endpoint_label                 = each.value.private_endpoint_label != null ? each.value.private_endpoint_label : null
  refreshable_mode                       = each.value.refreshable_mode != null ? each.value.refreshable_mode : null
  remote_disaster_recovery_type          = each.value.remote_disaster_recovery_type != null ? each.value.remote_disaster_recovery_type : null
  time_of_auto_refresh_start             = each.value.time_of_auto_refresh_start != null ? each.value.time_of_auto_refresh_start : null
  timestamp                              = each.value.timestamp != null ? each.value.timestamp : null
  use_latest_available_backup_time_stamp = each.value.use_latest_available_backup_time_stamp != null ? each.value.use_latest_available_backup_time_stamp : null
  whitelisted_ips                                            = each.value.whitelisted_ips != null ? each.value.whitelisted_ips : null

}
