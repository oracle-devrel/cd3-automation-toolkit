// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Network
# Create Dynamic Routing Gateway
############################

resource "oci_core_drg" "drg" {

  #Required
  compartment_id = var.compartment_id

  #Optional
  defined_tags  = var.defined_tags
  display_name  = var.display_name
  freeform_tags = var.freeform_tags

}