// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Governance
# Create Tag Key
############################

resource "oci_identity_tag" "tag" {
  #Required
  description      = var.description
  name             = var.name
  tag_namespace_id = var.tag_namespace_id

  #Optional
  defined_tags     = var.defined_tags
  freeform_tags    = var.freeform_tags
  is_cost_tracking = var.is_cost_tracking
  dynamic "validator" {
    for_each = try((var.tag_keys[var.key_name].validator[0].validator_type != "" ? var.tag_keys[var.key_name].validator : []), [])
    content {
      #Required
      validator_type = validator.value.validator_type
      values         = validator.value.validator_values
    }
  }
  is_retired = var.is_retired
}