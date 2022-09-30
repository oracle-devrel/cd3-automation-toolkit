// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Data Block - Network Load Balancer
# Create Network Load Balancer
#######################################

locals {
  nsg_ids = flatten(tolist([for nsg in var.network_security_group_ids : (length(regexall("ocid1.networksecuritygroup.oc1*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)]))
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each       = { for nsg in var.network_security_group_ids : nsg => nsg }
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = data.oci_core_vcns.oci_vcns_nlbs.virtual_networks[0].id
}

data "oci_core_vcns" "oci_vcns_nlbs" {
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = var.vcn_name
}

data "oci_core_subnets" "oci_subnets_nlbs" {
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = var.subnet_id
  vcn_id         = data.oci_core_vcns.oci_vcns_nlbs.virtual_networks[0].id
}

