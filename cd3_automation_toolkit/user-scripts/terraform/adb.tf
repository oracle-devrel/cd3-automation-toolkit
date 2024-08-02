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
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_adb[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_adb" {
  # depends_on = [module.vcns] # Uncomment to create Network and FSS together
  #for_each       = var.adb != null ? var.adb : {}
  for_each       = { for k, v in var.adb : k => v if v.vcn_name != null }
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "adb" {
  source   = "./modules/database/adb"
  for_each = var.adb != null ? var.adb : {}
  # depends_on = [module.nsgs]
  admin_password             = each.value.admin_password
  character_set              = each.value.character_set
  compartment_id             = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  cpu_core_count             = each.value.cpu_core_count
  database_edition           = each.value.database_edition
  data_storage_size_in_tbs   = each.value.data_storage_size_in_tbs
  db_name                    = each.value.db_name
  db_version                 = each.value.db_version
  db_workload                = each.value.db_workload
  defined_tags               = each.value.defined_tags
  display_name               = each.value.display_name
  license_model              = each.value.license_model
  ncharacter_set             = each.value.ncharacter_set
  customer_contacts          = each.value.customer_contacts
  network_compartment_id     = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  network_security_group_ids = each.value.nsg_ids
  freeform_tags              = each.value.freeform_tags
  subnet_id                  = each.value.subnet_id != null ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_adb[each.key].subnets.*.id[0]) : null
  vcn_name                   = each.value.vcn_name != null ? each.value.vcn_name : null
  whitelisted_ips            = each.value.whitelisted_ips

  #Optional parameters for ADB
  # are_primary_whitelisted_ips_used = var.autonomous_database_are_primary_whitelisted_ips_used
  # autonomous_container_database_id = oci_database_autonomous_container_database.test_autonomous_container_database.id
  # autonomous_database_backup_id = oci_database_autonomous_database_backup.test_autonomous_database_backup.id
  # autonomous_database_id = oci_database_autonomous_database.test_autonomous_database.id
  # autonomous_maintenance_schedule_type = var.autonomous_database_autonomous_maintenance_schedule_type
  # clone_type = var.autonomous_database_clone_type
  # customer_contacts {

  #Optional
  #     email = var.autonomous_database_customer_contacts_email
  # }
  # data_safe_status = var.autonomous_database_data_safe_status
  # data_storage_size_in_gb = var.autonomous_database_data_storage_size_in_gb
  # is_access_control_enabled = var.autonomous_database_is_access_control_enabled
  # is_auto_scaling_enabled = var.autonomous_database_is_auto_scaling_enabled
  # is_auto_scaling_for_storage_enabled = var.autonomous_database_is_auto_scaling_for_storage_enabled
  # is_data_guard_enabled = var.autonomous_database_is_data_guard_enabled
  # is_dedicated = var.autonomous_database_is_dedicated
  # is_free_tier = var.autonomous_database_is_free_tier
  # is_local_data_guard_enabled = var.autonomous_database_is_local_data_guard_enabled
  # is_mtls_connection_required = var.autonomous_database_is_mtls_connection_required
  # is_preview_version_with_service_terms_accepted = var.autonomous_database_is_preview_version_with_service_terms_accepted
  # kms_key_id = oci_kms_key.test_key.id
  # max_cpu_core_count = var.autonomous_database_max_cpu_core_count
  # ocpu_count = var.autonomous_database_ocpu_count
  # private_endpoint_label = var.autonomous_database_private_endpoint_label
  # refreshable_mode = var.autonomous_database_refreshable_mode
  # scheduled_operations {
  #     #Required
  #     day_of_week {
  #         #Required
  #         name = var.autonomous_database_scheduled_operations_day_of_week_name
  #     }

  #     #Optional
  #     scheduled_start_time = var.autonomous_database_scheduled_operations_scheduled_start_time
  #     scheduled_stop_time = var.autonomous_database_scheduled_operations_scheduled_stop_time
  # }
  # source = var.autonomous_database_source
  # source_id = oci_database_source.test_source.id
  # standby_whitelisted_ips = var.autonomous_database_standby_whitelisted_ips
  # timestamp = var.autonomous_database_timestamp
  # vault_id = oci_kms_vault.test_vault.id
  # whitelisted_ips = var.autonomous_database_whitelisted_ips

}