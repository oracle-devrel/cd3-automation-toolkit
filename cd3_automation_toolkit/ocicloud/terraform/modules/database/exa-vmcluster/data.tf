# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - Database
# Create ExaVMClusters
#############################

locals {
  nsg_ids        = var.nsg_ids != null ? flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups_db_exacs[nsg].network_security_groups[*].id)])) : null
  backup_nsg_ids = var.backup_network_nsg_ids != null ? flatten(tolist([for nsg in var.backup_network_nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups_backup_db_exacs[nsg].network_security_groups[*].id)])) : null
  db_servers     = flatten(toset([for server in data.oci_database_db_servers.all_db_servers : server.db_servers[*].id ]))
}

data "oci_core_vcns" "oci_vcns_db_exacs" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}


data "oci_core_network_security_groups" "network_security_groups_db_exacs" {
  for_each       = var.nsg_ids != null ? { for nsg in var.nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_db_exacs[var.vcn_names[0]].virtual_networks.*.id[0]
}

data "oci_core_network_security_groups" "network_security_groups_backup_db_exacs" {
  for_each       = var.backup_network_nsg_ids != null ? { for nsg in var.backup_network_nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_db_exacs[var.vcn_names[0]].virtual_networks.*.id[0]
}

data "oci_database_db_servers" "all_db_servers" {
  #Required
  for_each = toset(var.db_servers)
    compartment_id = var.compartment_id
    exadata_infrastructure_id = var.exadata_infrastructure_id

    #Optional
    filter {
    name   = "display_name"
    values = [each.key]
  }
    state = "AVAILABLE"
}