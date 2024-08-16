# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create VLANs
############################

resource "oci_core_vlan" "vlan" {
  cidr_block          = var.cidr_block
  compartment_id      = var.compartment_id
  vcn_id              = var.vcn_id
  display_name        = var.display_name
  nsg_ids             = var.nsg_ids != null ? (local.nsg_ids == [] ? ["INVALID NSG Name"] : local.nsg_ids) : []
  route_table_id      = var.route_table_id
  vlan_tag            = var.vlan_tag
  availability_domain = var.availability_domain

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}
