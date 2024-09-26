# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
data "oci_core_vcns" "firewall_vcn" {
  compartment_id = var.compartment_id != null ? var.compartment_id : var.compartment_id
  display_name = var.vcn_name != null ? var.vcn_name : var.vcn_name
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each = var.nsg_id != null ? { for nsg in var.nsg_id : nsg => nsg } : {}
  compartment_id = var.compartment_id != null ? var.compartment_id : var.compartment_id
  display_name = each.value
  vcn_id = data.oci_core_vcns.firewall_vcn.virtual_networks.*.id[0]
}


locals {
  nsg_id = var.nsg_id != null ? flatten(tolist([for nsg in var.nsg_id : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id) ])) : null
}



/*
output "nsgid" {
  value = data.oci_core_network_security_groups.network_security_groups
}*/