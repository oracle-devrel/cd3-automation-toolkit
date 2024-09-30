# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
      for_each = var.actions[var.key_name]["actions"] != [] ? var.actions[var.key_name]["actions"] : []
      content {
        #Required
        action_type = actions.value.action_type
        is_enabled  = actions.value.is_enabled

        #Optional
        description = actions.value.description != "" ? actions.value.description : null
        function_id = actions.value.function_id
        stream_id   = actions.value.stream_id
        topic_id    = (actions.value.topic_id != "" && actions.value.topic_id != null) ? (length(regexall("ocid1.onstopic.oc*", actions.value.topic_id)) > 0 ? actions.value.topic_id : var.topic_name[actions.value.topic_id]["topic_tf_id"]) : null
      }
    }
  }

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}
