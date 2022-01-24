// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - ManagementServices
# Create Events
############################

resource "oci_events_rule" "rule" {
  count = var.event_name != null ? 1 : 0
  #Required
  compartment_id = var.compartment_name
  display_name   = var.event_name

  is_enabled     = var.is_enabled
  description    = var.description
  condition      = var.condition
  actions        = var.actions

  #Optional
  defined_tags = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
    }
}
