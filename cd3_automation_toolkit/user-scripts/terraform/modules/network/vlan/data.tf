# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
## Data Block - VLAN
## Create VLANs
#############################

locals {
  nsg_ids = var.nsg_ids != null ? flatten(tolist([for nsg in var.nsg_ids : (length(regexall("ocid1.networksecuritygroup.oc*", nsg)) > 0 ? [nsg] : data.oci_core_network_security_groups.network_security_groups[nsg].network_security_groups[*].id)])) : null
}

data "oci_core_network_security_groups" "network_security_groups" {
  for_each       = var.nsg_ids != null ? { for nsg in var.nsg_ids : nsg => nsg } : {}
  compartment_id = var.network_compartment_id != null ? var.network_compartment_id : var.compartment_id
  display_name   = each.value
  vcn_id         = var.vcn_id
}

data "oci_core_vcn" "vcns" {
  #Required
  vcn_id = var.vcn_id
}