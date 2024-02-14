// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Identity
# Create Compartments
############################

resource "oci_identity_compartment" "compartment" {

  #Required
  compartment_id = var.compartment_id != null ? var.compartment_id : var.tenancy_ocid
  description    = var.compartment_description
  name           = var.compartment_name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  enable_delete = var.enable_delete

}
