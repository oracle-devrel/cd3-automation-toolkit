// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - Storage
# Create FSS
############################

module "mts" {
  #Required
  source   = "./modules/storage/file-storage-service/mount-target"
  for_each = (var.mount_targets != null || var.mount_targets != {}) ? var.mount_targets : {}
  #Required
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
  network_compartment_id = each.value.network_compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.network_compartment_name)) > 0 ? each.value.network_compartment_name : var.compartment_ocids[each.value.network_compartment_name]) : var.compartment_ocids[each.value.network_compartment_name]

  subnet_id = each.value.subnet_name
  vcn_names = [each.value.vcn_name]

  #Optional
  defined_tags = each.value.defined_tags
  display_name = each.value.display_name != null ? each.value.display_name : null
  freeform_tags = each.value.freeform_tags
  hostname_label = each.value.hostname_label
  ip_address = each.value.ip_address
  #nsg_ids = [for nsg in each.value.nsg_ids : length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : merge(module.nsgs.*...)[nsg]["nsg_tf_id"]]
  #nsg_ids = each.value.nsg_ids == [] ? null : ([for nsg in each.value.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc1*",nsg)) > 0 ? nsg : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)])
  network_security_group_ids = each.value.nsg_ids == [] ? null : each.value.nsg_ids

}

module "fss" {
  #Required
  source   = "./modules/storage/file-storage-service/fss"
  for_each = (var.fss != null || var.fss != {}) ? var.fss : {}

  #Required
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null

  #Optional
  defined_tags  = each.value.defined_tags
  display_name  = each.value.display_name != null ? each.value.display_name : null
  freeform_tags = each.value.freeform_tags
  kms_key_id = each.value.kms_key_name
  source_snapshot_id = each.value.source_snapshot_name
}

module "fss-export-options" {
  #Required
  source   = "./modules/storage/file-storage-service/export-option"
  for_each = (var.nfs_export_options != null || var.nfs_export_options != {}) ? var.nfs_export_options : {}

  #Required
  export_set_id = length(regexall("ocid1.mounttarget.oc1*", each.value.export_set_id)) > 0 ? each.value.export_set_id : merge(module.mts.*...)[each.value.export_set_id]["mt_exp_set_id"]
  file_system_id = length(regexall("ocid1.filesystem.oc1*", each.value.file_system_id)) > 0 ? each.value.file_system_id : merge(module.fss.*...)[each.value.file_system_id]["fss_tf_id"]
  export_path = each.value.path
  nfs_export_options = var.nfs_export_options
  key_name = each.key
}
