# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Network
# Create NAT Gateway
############################

resource "oci_core_nat_gateway" "nat_gateway" {

  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  block_traffic = var.block_traffic
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags
  public_ip_id  = var.public_ip_id
  route_table_id = var.route_table_id

}