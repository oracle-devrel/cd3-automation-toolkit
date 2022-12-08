// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Internet Gateway
############################

resource "oci_core_internet_gateway" "internet_gateway" {

  #Required
  compartment_id = var.compartment_id
  vcn_id         = var.vcn_id

  #Optional
  enabled        = var.enabled
  defined_tags   = var.defined_tags
  display_name   = var.display_name
  freeform_tags  = var.freeform_tags
  route_table_id = var.route_table_id

}