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
  unique_log_groups = {
    for key in distinct([
      for item in var.log_group_names : "${item.compartment_id}@${item.log_group_id}"]) : key => {
      compartment_id = split("@", key)[0]
      log_group_id   = split("@", key)[1]
    }
  }

  resolved_log_group_ids = [
    for item in var.log_group_names : {
      compartment_id = item.compartment_id
      log_group_id   = length(regexall("Audit", item.log_group_id)) > 0 ? (length(regexall("Audit_In_Subcompartment", item.log_group_id)) > 0 ? "_Audit_Include_Subcompartment" : "_Audit") : data.oci_logging_log_groups.source_log_groups["${item.compartment_id}@${item.log_group_id}"].log_groups[0].id
      log_id_name    = item.log_id
    }
  ]

  source_log_group_detail = [
    for item in local.resolved_log_group_ids : {
      compartment_id = item.compartment_id
      log_group_id   = item.log_group_id
      log_id         = lower(item.log_id_name) == "all" ? null : data.oci_logging_logs.source_logs["${item.log_group_id}@${item.log_id_name}"].logs[0].id
    }
  ]

  # creating ordered map
  n = length(local.source_log_group_detail)
  # Number of groups of 10 items
  groups_count = ceil(local.n / 10)
  prefixes = [
    for i in range(local.groups_count) : join("", [for _ in range(i) : "9"])
  ]
  # Now create keys by combining prefix + digit (0-9), flatten the list, but only up to n keys
  keys = slice(flatten([
    for prefix in local.prefixes : [
      for digit in range(10) : "${prefix}${digit}"
    ]
  ]), 0, local.n)
  indexed_map = {
    for idx in range(local.n) :
    local.keys[idx] => local.source_log_group_detail[idx]
  }
  # local ends here
}

#output "first_level_logs" {

#value  = local.indexed_map #local.source_log_group_detail

#}

data "oci_logging_log_groups" "source_log_groups" {
  for_each       = local.unique_log_groups
  compartment_id = each.value.compartment_id
  display_name   = each.value.log_group_id
}

data "oci_logging_logs" "source_logs" {
  for_each = {
    for item in distinct(local.resolved_log_group_ids) :
    "${item.log_group_id}@${item.log_id_name}" => item
  if lower(item.log_id_name) != "all" }
  log_group_id = each.value.log_group_id
  display_name = each.value.log_id_name
}

data "oci_objectstorage_namespace" "os_namespace" {
  compartment_id = var.logs_compartment_id
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