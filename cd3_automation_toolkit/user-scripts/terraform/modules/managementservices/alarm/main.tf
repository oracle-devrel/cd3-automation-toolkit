// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - ManagementServices
# Create Alarms
############################

resource "oci_monitoring_alarm" "alarm" {

  # Required
  compartment_id        = var.compartment_id
  display_name          = var.alarm_name
  destinations          = var.destinations
  is_enabled            = var.is_enabled
  metric_compartment_id = var.metric_compartment_id
  namespace             = var.namespace
  query                 = var.query
  severity              = var.severity
  body                  = var.body

  message_format        = var.message_format
  #metric_compartment_id_in_subtree = var.alarm_metric_compartment_id_in_subtree
  pending_duration             = var.trigger_delay_minutes
  repeat_notification_duration = var.repeat_notification_duration

  #resolution = var.alarm_resolution
  #resource_group = var.alarm_resource_group
  #suppression {
  #Required
  #    time_suppress_from = var.alarm_suppression_time_suppress_from
  #    time_suppress_until = var.alarm_suppression_time_suppress_until

  #Optional
  #    description = var.alarm_suppression_description
  #}

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}
