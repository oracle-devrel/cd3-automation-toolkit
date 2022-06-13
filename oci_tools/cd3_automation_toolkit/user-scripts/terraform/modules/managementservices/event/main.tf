// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - ManagementServices
# Create Events
############################

resource "oci_events_rule" "event" {

  #Required
  compartment_id = var.compartment_id
  display_name   = var.event_name

  is_enabled  = var.is_enabled
  description = var.description
  condition   = var.condition
  actions {
    dynamic "actions" {
      for_each = var.actions[var.key_name]["actions"] != [] ? var.actions[var.key_name]["actions"] : null
      content {
        #Required
        action_type = actions.value.action_type
        is_enabled  = actions.value.is_enabled

        #Optional
        description = actions.value.description
        function_id = (actions.value.function_id != "" && actions.value.function_id != null) ? actions.value.function_id : null
        stream_id   = (actions.value.stream_id != "" && actions.value.stream_id != null) ? actions.value.stream_id : null
        topic_id    = (actions.value.topic_id != "" && actions.value.topic_id != null) ? (length(regexall("ocid1.onstopic.oc1*", actions.value.topic_id)) > 0 ? actions.value.topic_id : var.topic_name[actions.value.topic_id]["topic_tf_id"]) : null
      }
    }
  }

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
