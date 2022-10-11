// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Governance
# Create Tag Defaults
############################

resource "oci_identity_tag_default" "tag_default" {
  #Required
  compartment_id    = var.compartment_id
  tag_definition_id = var.tag_definition_id
  value             = var.value

  #Optional
  is_required = var.is_required
}