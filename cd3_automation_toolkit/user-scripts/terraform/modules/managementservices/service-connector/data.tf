# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
####################################
# Data Block - Service Connector
# Create Service Connector Hub
#####################################

locals {
  log_group_names = var.log_group_names
  source_kind     = var.source_kind
  filtered_logs   = [for item in var.log_group_names : item if split("@", item)[2] != "all"]
}

data "oci_objectstorage_namespace" "os_namespace" {
  compartment_id = var.logs_compartment_id
}
data "oci_identity_compartments" "all_compartments" {
  #Required
  compartment_id            = var.logs_compartment_id
  compartment_id_in_subtree = true
}
data "oci_streaming_streams" "source_streams" {
  for_each       = var.source_stream_id
  name           = each.value
  compartment_id = each.key
}
data "oci_streaming_streams" "target_streams" {
  for_each       = var.stream_id
  name           = each.value
  compartment_id = each.key
}
data "oci_ons_notification_topics" "target_topics" {
  for_each       = var.topic_id
  name           = each.value
  compartment_id = each.key
}
data "oci_logging_log_groups" "source_log_groups" {
  for_each       = toset(var.log_group_names)
  compartment_id = split("@", each.key)[0]
  display_name   = split("@", each.key)[1]
}
data "oci_logging_logs" "source_logs" {
  for_each     = toset(local.filtered_logs)
  log_group_id = data.oci_logging_log_groups.source_log_groups[each.key].log_groups[0].id
  display_name = split("@", each.key)[2]
}
data "oci_log_analytics_log_analytics_log_groups" "target_log_analytics_log_groups" {
  for_each = var.destination_log_group_id
  #Required
  compartment_id = each.key
  namespace      = data.oci_objectstorage_namespace.os_namespace.namespace

  #Optional
  display_name = each.value
}

data "oci_functions_applications" "applications" {
  for_each = toset(var.function_details)
  #Required
  compartment_id = split("@", each.key)[0]

  #Optional
  display_name = split("@", each.key)[1]
}

data "oci_functions_functions" "functions" {
  for_each = toset(var.function_details)
  #Required
  application_id = data.oci_functions_applications.applications[each.key].applications[0].id

  #Optional
  display_name = split("@", each.key)[2]
}

data "oci_identity_compartments" "compartments" {
  for_each = toset(keys(var.source_monitoring_details))
  #Required
  compartment_id = var.logs_compartment_id

  #Optional
  access_level              = "ANY"
  compartment_id_in_subtree = true
  state                     = "ACTIVE"
  name                      = each.value
}