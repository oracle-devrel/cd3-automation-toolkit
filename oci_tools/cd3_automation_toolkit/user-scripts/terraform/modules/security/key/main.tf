// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
    #curve_id = oci_kms_curve.test_curve.id
  }
  management_endpoint = var.management_endpoint

  #Optional
  defined_tags    = var.defined_tags
  freeform_tags   = var.freeform_tags
  protection_mode = var.protection_mode != "" ? var.protection_mode : null

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}