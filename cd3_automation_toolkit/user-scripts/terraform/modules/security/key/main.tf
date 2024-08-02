# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Security
## Create Key
################################

resource "oci_kms_key" "key" {
  #Required
  compartment_id = var.compartment_id
  display_name   = var.display_name
  key_shape {
    #Required
    algorithm = var.algorithm
    length    = var.length

    #Optional
    curve_id = var.curve_id
  }
  management_endpoint = var.management_endpoint

  #Optional
  defined_tags    = var.defined_tags
  freeform_tags   = var.freeform_tags
  protection_mode = var.protection_mode != "" ? var.protection_mode : null
  is_auto_rotation_enabled = var.is_auto_rotation_enabled
  dynamic "auto_key_rotation_details" {
    for_each = coalesce(var.is_auto_rotation_enabled, false) ? [1] : []
    content {
      rotation_interval_in_days = var.rotation_interval_in_days
    }
  }
}