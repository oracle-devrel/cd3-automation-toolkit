# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Storage
# Create FSS
############################

data "oci_core_subnets" "oci_subnets_fss" {
  # depends_on = [module.subnets] # Uncomment to create Network and FSS together
  for_each       = var.mount_targets != null ? var.mount_targets : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_fss[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_vcns_fss" {
  # depends_on = [module.vcns] # Uncomment to create Network and FSS together
  for_each       = var.mount_targets != null ? var.mount_targets : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "mts" {
  # depends_on = [module.nsgs] # Uncomment to execute NSG and Mount Target together
  #Required
  source   = "./modules/storage/file-storage/mount-target"
  for_each = (var.mount_targets != null || var.mount_targets != {}) ? var.mount_targets : {}
  #Required
  availability_domain    = each.value.availability_domain != null && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : null
  compartment_id         = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  subnet_id              = length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_subnets_fss[each.key].subnets.*.id[0]
  vcn_names              = [each.value.vcn_name]

  #Optional
  defined_tags   = each.value.defined_tags
  display_name   = each.value.display_name
  freeform_tags  = each.value.freeform_tags
  hostname_label = each.value.hostname_label
  ip_address     = each.value.ip_address
  #nsg_ids = [for nsg in each.value.nsg_ids : length(regexall("ocid1.networksecuritygroup.oc*",nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"]]
  #nsg_ids = each.value.nsg_ids == [] ? null : ([for nsg in each.value.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*",nsg)) > 0 ? nsg : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)])
  network_security_group_ids = each.value.nsg_ids
}

module "fss" {
  #Required
  source   = "./modules/storage/file-storage/fss"
  for_each = (var.fss != null || var.fss != {}) ? var.fss : {}

  #Required
  availability_domain = each.value.availability_domain != null && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : null
  compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags                  = each.value.defined_tags
  display_name                  = each.value.display_name
  freeform_tags                 = each.value.freeform_tags
  kms_key_id                    = each.value.kms_key_id
  source_snapshot_id            = each.value.source_snapshot != null ? (length(regexall("ocid1.snapshot.oc*", each.value.source_snapshot)) > 0 ? each.value.source_snapshot : lookup(var.fss_source_ocids, each.value.source_snapshot, null)) : null
  filesystem_snapshot_policy_id = each.value.snapshot_policy
  policy_compartment_id         = each.value.policy_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.policy_compartment_id)) > 0 ? each.value.policy_compartment_id : var.compartment_ocids[each.value.policy_compartment_id]) : var.compartment_ocids[each.value.compartment_id]
}

module "fss-export-options" {
  #Required
  source   = "./modules/storage/file-storage/export-option"
  for_each = (var.nfs_export_options != null || var.nfs_export_options != {}) ? var.nfs_export_options : {}

  #Required
  export_set_id      = length(regexall("ocid1.mounttarget.oc*", each.value.export_set_id)) > 0 ? each.value.export_set_id : merge(module.mts.*...)[each.value.export_set_id]["mt_exp_set_id"]
  file_system_id     = length(regexall("ocid1.filesystem.oc*", each.value.file_system_id)) > 0 ? each.value.file_system_id : merge(module.fss.*...)[each.value.file_system_id]["fss_tf_id"]
  export_path        = each.value.path
  nfs_export_options = var.nfs_export_options
  key_name           = each.key
}

module "fss-replication" {
  #Required
  source   = "./modules/storage/file-storage/fss-replication"
  for_each = (var.fss_replication != null || var.fss_replication != {}) ? var.fss_replication : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  source_id      = length(regexall("ocid1.filesystem.oc*", each.value.source_id)) > 0 ? each.value.source_id : merge(module.fss.*...)[each.value.source_id]["fss_tf_id"]
  target_id      = length(regexall("ocid1.filesystem.oc*", each.value.target_id)) > 0 ? each.value.target_id : merge(module.fss.*...)[each.value.target_id]["fss_tf_id"]
  #Optional
  defined_tags         = each.value.defined_tags
  display_name         = each.value.display_name
  freeform_tags        = each.value.freeform_tags
  replication_interval = each.value.replication_interval

}

#############################
# Module Block - FSS Logging
# Create Log Groups and Logs
#############################

module "nfs-log-groups" {
  source   = "./modules/managementservices/log-group"
  for_each = (var.nfs_log_groups != null || var.nfs_log_groups != {}) ? var.nfs_log_groups : {}

  # Log Groups
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  display_name = each.value.display_name

  #Optional
  defined_tags  = each.value.defined_tags
  description   = each.value.description
  freeform_tags = each.value.freeform_tags
}

/*
output "log_group_map" {
  value = [ for k,v in merge(module.loadbalancer-log-groups.*...) : v.log_group_tf_id ]
}
*/

module "nfs-logs" {
  source   = "./modules/managementservices/log"
  for_each = (var.nfs_logs != null || var.nfs_logs != {}) ? var.nfs_logs : {}

  # Logs
  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  display_name   = each.value.display_name
  log_group_id   = length(regexall("ocid1.loggroup.oc*", each.value.log_group_id)) > 0 ? each.value.log_group_id : merge(module.nfs-log-groups.*...)[each.value.log_group_id]["log_group_tf_id"]

  log_type = each.value.log_type
  #Required
  source_category        = each.value.category
  source_resource        = length(regexall("ocid1.*", each.value.resource)) > 0 ? each.value.resource : merge(module.mts.*...)[each.value.resource]["mt_tf_id"]
  source_service         = each.value.service
  source_type            = each.value.source_type
  defined_tags           = each.value.defined_tags
  freeform_tags          = each.value.freeform_tags
  log_is_enabled         = (each.value.is_enabled == "" || each.value.is_enabled == null) ? true : each.value.is_enabled
  log_retention_duration = (each.value.retention_duration == "" || each.value.retention_duration == null) ? 30 : each.value.retention_duration

}

/*
output "logs_id" {
  value = [ for k,v in merge(module.loadbalancer-logs.*...) : v.log_tf_id]
}
*/
