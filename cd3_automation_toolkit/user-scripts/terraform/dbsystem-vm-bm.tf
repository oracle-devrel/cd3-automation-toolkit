# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block - Database
# Create DB Systems VM BM
############################################
data "oci_core_subnets" "oci_dbsystems_subnets" {
  # depends_on = [module.subnets] # Uncomment to create Network and Instances together
  for_each       = var.dbsystems_vm_bm != null ? var.dbsystems_vm_bm : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.subnet_id
  vcn_id         = data.oci_core_vcns.oci_dbsystems_vcns[each.key].virtual_networks.*.id[0]
}

data "oci_core_vcns" "oci_dbsystems_vcns" {
  # depends_on = [module.vcns] # Uncomment to create Network and Instances together
  for_each       = var.dbsystems_vm_bm != null ? var.dbsystems_vm_bm : {}
  compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : var.compartment_ocids[each.value.network_compartment_id]
  display_name   = each.value.vcn_name
}

module "dbsystems-vm-bm" {
  source = "./modules/database/dbsystem-vm-bm"
  # depends_on = [module.nsgs] # Uncomment to create NSG and DB Systems together
  for_each            = var.dbsystems_vm_bm != null ? var.dbsystems_vm_bm : {}
  availability_domain = each.value.availability_domain != "" && each.value.availability_domain != null ? data.oci_identity_availability_domains.availability_domains.availability_domains[each.value.availability_domain].name : ""
  compartment_id      = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  hostname            = each.value.hostname
  display_name        = each.value.display_name
  db_version          = each.value.db_version
  cluster_name        = each.value.cluster_name
  shape               = each.value.shape
  #ssh_public_key     = length(regexall("ssh-rsa*",each.value.ssh_public_key)) > 0 ? each.value.ssh_public_key : var.ssh_public_key
  ssh_public_keys        = lookup(var.dbsystem_ssh_keys, each.value.ssh_public_keys, var.dbsystem_ssh_keys["ssh_public_key"])
  network_compartment_id = each.value.network_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.network_compartment_id)) > 0 ? each.value.network_compartment_id : var.compartment_ocids[each.value.network_compartment_id]) : null
  vcn_names              = [each.value.vcn_name]
  subnet_id              = each.value.subnet_id != "" ? (length(regexall("ocid1.subnet.oc*", each.value.subnet_id)) > 0 ? each.value.subnet_id : data.oci_core_subnets.oci_dbsystems_subnets[each.key].subnets.*.id[0]) : null
  node_count             = each.value.node_count
  nsg_ids                = each.value.nsg_ids != null ? each.value.nsg_ids : []

  time_zone               = each.value.time_zone
  cpu_core_count          = each.value.cpu_core_count
  database_edition        = each.value.database_edition
  data_storage_size_in_gb = each.value.data_storage_size_in_gb
  data_storage_percentage = each.value.data_storage_percentage
  disk_redundancy         = each.value.disk_redundancy
  license_model           = each.value.license_model
  pdb_name                = each.value.pdb_name
  db_name                 = each.value.db_name
  db_home_display_name    = each.value.db_home_display_name
  admin_password          = each.value.admin_password
  db_workload             = each.value.db_workload
  auto_backup_enabled     = each.value.auto_backup_enabled
  character_set           = each.value.character_set
  ncharacter_set          = each.value.ncharacter_set
  recovery_window_in_days = each.value.recovery_window_in_days
  defined_tags            = each.value.defined_tags
  freeform_tags           = each.value.freeform_tags

}