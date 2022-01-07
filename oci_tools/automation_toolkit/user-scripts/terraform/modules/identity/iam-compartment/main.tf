// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Identity
# Create Compartments
############################

resource "oci_identity_compartment" "compartment" {
  count          = var.compartment_create ? 1 : 0
  #Required
  compartment_id = var.compartment_id != null ? var.compartment_id : var.tenancy_ocid
  name           = var.compartment_name
  description    = var.compartment_description

  #Optional
  defined_tags = var.defined_tags
  freeform_tags = var.freeform_tags
  #enable_delete  = var.enable_delete
  
  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
    }
}
