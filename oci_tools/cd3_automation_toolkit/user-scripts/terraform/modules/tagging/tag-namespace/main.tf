// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Governance
# Create Namespaces
############################

resource "oci_identity_tag_namespace" "tag_namespace" {
  #Required
  compartment_id = var.compartment_id != null ? var.compartment_id : var.tenancy_ocid
  description    = var.description
  name           = var.name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
  is_retired    = var.is_retired
}