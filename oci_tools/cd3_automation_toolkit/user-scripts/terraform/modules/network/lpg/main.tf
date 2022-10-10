// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Local Peering Gateway
############################

resource "oci_core_local_peering_gateway" "local_peering_gateway" {

  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  freeform_tags  = var.freeform_tags
  peer_id        = var.peer_id
  route_table_id = var.route_table_id

}