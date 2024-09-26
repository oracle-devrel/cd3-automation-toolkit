# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create Groups
############################
locals {
  user_ids = {
    for user in data.oci_identity_users.users.users :
      user.name => user.id
  }
}
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
resource "oci_identity_user_group_membership" "user_group_membership" {
  for_each = {
    for member in var.members : member => member
  }
  group_id = oci_identity_group.group[0].id
  user_id  = local.user_ids[each.key]
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