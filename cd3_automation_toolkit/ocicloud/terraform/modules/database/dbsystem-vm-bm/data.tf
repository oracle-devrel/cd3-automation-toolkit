# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - Database
# Create ExaVMClusters
#############################

locals {
  nsg_ids = var.nsg_ids != null ? flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups_dbsystems[nsg].network_security_groups[*].id)])) : null
}

data "oci_core_vcns" "oci_vcns_dbsystems" {
  for_each       = { for vcn in var.vcn_names : vcn => vcn }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
}


data "oci_core_network_security_groups" "network_security_groups_dbsystems" {
  for_each       = var.nsg_ids != null ? { for nsg in var.nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_dbsystems[var.vcn_names[0]].virtual_networks.*.id[0]
}
