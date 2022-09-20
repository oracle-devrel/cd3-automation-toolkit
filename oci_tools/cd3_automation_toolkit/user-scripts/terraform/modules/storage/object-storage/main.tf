// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
  access_type           = var.access_type
  auto_tiering          = var.auto_tiering
  freeform_tags         = var.freeform_tags
  defined_tags          = var.defined_tags
  kms_key_id            = var.kms_key_id
  metadata              = var.metadata
  object_events_enabled = var.object_events_enabled
  storage_tier          = var.storage_tier

  dynamic "retention_rules" {
    for_each = var.retention_rules != [] ? var.retention_rules : []
    content {
      display_name = retention_rules.value.display_name

      dynamic "duration" {
        for_each = retention_rules.value.duration != [] ? retention_rules.value.duration : []
        content {
          #Required
          time_amount = duration.value.time_amount
          time_unit   = duration.value.time_unit
        }
      }

      time_rule_locked = retention_rules.value.time_rule_locked
    }
  }

  versioning = var.versioning

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"], freeform_tags]
  }
}