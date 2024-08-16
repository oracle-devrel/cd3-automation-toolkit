# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Object Storage
## Create Object Storage
################################

resource "oci_objectstorage_bucket" "bucket" {
  #Required
  compartment_id = var.compartment_id
  name           = var.name
  namespace      = var.namespace

  #Optional
  access_type   = var.access_type
  auto_tiering  = var.auto_tiering
  freeform_tags = var.freeform_tags
  defined_tags  = var.defined_tags
  kms_key_id            = var.kms_key_id
  #metadata              = var.metadata
  object_events_enabled = var.object_events_enabled
  storage_tier          = var.storage_tier

  dynamic "retention_rules" {
    for_each = var.retention_rules != null ? var.retention_rules : []
    content {
      #Required
      display_name = retention_rules.value.display_name
      dynamic "duration" {
        for_each = try(retention_rules.value.duration, [])
        content {
          #Required
          time_amount = duration.value.time_amount
          time_unit   = duration.value.time_unit
        }
      }
      time_rule_locked = try(retention_rules.value.time_rule_locked, null)

    }
  }
  versioning = var.versioning
  lifecycle {
    ignore_changes = [metadata]
  }
}

resource "oci_objectstorage_replication_policy" "replication_policy" {
  count = length(var.replication_policy) > 0 ? 1 : 0

  #Required
  depends_on              = [resource.oci_objectstorage_bucket.bucket]
  bucket                  = var.bucket
  namespace               = var.namespace
  name                    = var.replication_policy["name"]
  destination_bucket_name = var.replication_policy["destination_bucket_name"]
  destination_region_name = var.replication_policy["destination_region_name"]

}

resource "oci_objectstorage_object_lifecycle_policy" "lifecycle_policy" {
  count      = length(var.rules) > 0 ? 1 : 0
  depends_on = [resource.oci_objectstorage_bucket.bucket]
  bucket     = var.bucket
  namespace  = var.namespace

  #Optional
  dynamic "rules" {
    for_each = var.rules
    content {
      action      = rules.value.action
      is_enabled  = rules.value.is_enabled
      name        = rules.value.name
      time_amount = rules.value.Time_Amount
      time_unit   = rules.value.Time_Unit
      # Create a local variable for the object_name_filter block
      dynamic "object_name_filter" {
        #for_each = rules.value.target != "multipart-uploads" ? [1] : []
        for_each = rules.value.target != "multipart-uploads" ? (rules.value.exclusion_patterns != [] || rules.value.inclusion_patterns != [] || rules.value.inclusion_prefixes != [] ? [1] : []) : []

        content {
          exclusion_patterns = rules.value.exclusion_patterns
          inclusion_patterns = rules.value.inclusion_patterns
          inclusion_prefixes = rules.value.inclusion_prefixes
        }
      }

      target = rules.value.target
    }
  }

}