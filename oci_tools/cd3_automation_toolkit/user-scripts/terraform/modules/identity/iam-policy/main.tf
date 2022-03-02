// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Resource Block - Identity
# Create Policies 
#############################

resource "oci_identity_policy" "policy" {

  # Required
  name           = var.policy_name
  description    = var.policy_description
  compartment_id = var.policy_compartment_id
  statements     = var.policy_statements

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], freeform_tags, description]
  }
}
