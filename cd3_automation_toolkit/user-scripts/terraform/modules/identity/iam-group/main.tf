# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create Groups
############################

resource "oci_identity_group" "group" {
  count = (var.matching_rule != "" && var.matching_rule != null) ? 0 : 1

  #Required
  compartment_id = var.tenancy_ocid
  description    = var.group_description
  name           = var.group_name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}

############################
# Resource Block - Identity
# Create Dynamic Groups
############################

resource "oci_identity_dynamic_group" "dynamic_group" {
  count = (var.matching_rule != "" && var.matching_rule != null) ? 1 : 0

  #Required
  compartment_id = var.tenancy_ocid
  description    = var.group_description
  matching_rule  = var.matching_rule
  name           = var.group_name

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}