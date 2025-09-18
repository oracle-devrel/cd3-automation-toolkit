# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create Groups
############################
locals {
  user_ids = {
    for user in data.oci_identity_domains_users.users.users :
      user.user_name => user.id...
  }
}

resource "oci_identity_domains_group" "group" {
  count = (var.matching_rule == "" || var.matching_rule == null) ? 1 : 0
  #Required
  display_name  = var.group_name
  attribute_sets = ["all"]
  attributes = "members"
  idcs_endpoint = var.identity_domain.url
  schemas       = [
    "urn:ietf:params:scim:schemas:core:2.0:Group",
    "urn:ietf:params:scim:schemas:oracle:idcs:extension:OCITags",
    "urn:ietf:params:scim:schemas:oracle:idcs:extension:group:Group",
  ]
  timeouts {}
  urnietfparamsscimschemasoracleidcsextensiongroup_group {
    description = var.group_description
  }

  dynamic "members" {
    for_each = {for k in var.members: k=>k}
    content {
      type  = "User"
      value = local.user_ids[members.value][0]
    }
  }
  dynamic "urnietfparamsscimschemasoracleidcsextensionrequestable_group" {
   for_each = var.user_can_request_access == false ?[1]:[]
    content {
    #Optional
    requestable = var.user_can_request_access
    }
}
  urnietfparamsscimschemasoracleidcsextension_oci_tags {

    # Optional
    dynamic "defined_tags" {
      for_each = var.defined_tags != null ? var.defined_tags : []
      content {
        key       = defined_tags.value.key
        namespace = defined_tags.value.namespace
        value     = defined_tags.value.value
      }
    }
    dynamic "freeform_tags" {
      for_each = var.freeform_tags_key != null && var.freeform_tags_value != null ? [1] : []
      content {
        key   = var.freeform_tags_key
        value = var.freeform_tags_value
      }
    }
  }

  # Add the lifecycle block to ignore changes to specified attributes
  lifecycle {
    ignore_changes = [
      schemas,
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedOn"],
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedBy"],
    ]
  }
}

############################
# Resource Block - Identity
# Create Dynamic Groups
############################

resource "oci_identity_domains_dynamic_resource_group" "dynamic_group" {
  count = (var.matching_rule != "" && var.matching_rule != null) ? 1 : 0

  #Required
  display_name  = var.group_name
  attribute_sets = ["all"]
  attributes = "matching_rule"
  idcs_endpoint = var.identity_domain.url
  matching_rule = var.matching_rule
  schemas       = [
    "urn:ietf:params:scim:schemas:oracle:idcs:DynamicResourceGroup",
    "urn:ietf:params:scim:schemas:oracle:idcs:extension:OCITags",
  ]
  description   = var.group_description
  timeouts {}

  urnietfparamsscimschemasoracleidcsextension_oci_tags {

    # Optional
    dynamic "defined_tags" {
      for_each = var.defined_tags != null ? var.defined_tags : []
      content {
        key       = defined_tags.value.key
        namespace = defined_tags.value.namespace
        value     = defined_tags.value.value
      }
    }

    dynamic "freeform_tags" {
      for_each = var.freeform_tags_key != null && var.freeform_tags_value != null ? [1] : []
      content {
        key   = var.freeform_tags_key
        value = var.freeform_tags_value
      }
    }
  }
  # Add the lifecycle block to ignore changes to specified attributes
  lifecycle {
    ignore_changes = [
      schemas,
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedOn"],
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedBy"],
    ]
  }
}

