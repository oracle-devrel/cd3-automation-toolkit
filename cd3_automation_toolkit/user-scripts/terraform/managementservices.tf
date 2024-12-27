# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - ManagementServices
# Create Alarms
############################

module "alarms" {
  source = "./modules/managementservices/alarm"

  depends_on = [module.notifications-topics]
  for_each   = var.alarms != null ? var.alarms : {}

  alarm_name                   = each.value.alarm_name
  compartment_id               = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  destinations                 = [for tn in each.value.destinations : (length(regexall("ocid1.onstopic.oc*", tn)) > 0 ? tn : merge(module.notifications-topics.*...)[tn]["topic_tf_id"])]
  is_enabled                   = each.value.is_enabled
  metric_compartment_id        = each.value.metric_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.metric_compartment_id)) > 0 ? each.value.metric_compartment_id : var.compartment_ocids[each.value.metric_compartment_id]) : null
  namespace                    = each.value.namespace
  query                        = each.value.query
  severity                     = each.value.severity
  body                         = each.value.body
  message_format               = each.value.message_format
  trigger_delay_minutes        = each.value.trigger_delay_minutes
  repeat_notification_duration = each.value.repeat_notification_duration

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "alarms_id" {
  value = [ for k,v in merge(module.alarms.*...) : v.alarm_tf_id]
}
*/

############################
# Module Block - ManagementServices
# Create Events
############################

module "events" {
  source     = "./modules/managementservices/event"
  depends_on = [module.notifications-topics]
  for_each   = var.events != null ? var.events : {}

  event_name     = each.value.event_name
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  is_enabled     = each.value.is_enabled
  description    = each.value.description
  condition      = each.value.condition
  actions        = var.events
  key_name       = each.key
  topic_name     = merge(module.notifications-topics.*...)

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "events_id" {
  value = [ for k,v in merge(module.events.*...) : v.event_tf_id]
}
*/

############################
# Module Block - ManagementServices
# Create Notifications
############################

module "notifications-topics" {
  source   = "./modules/managementservices/notification-topic"
  for_each = var.notifications_topics != null ? var.notifications_topics : {}

  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  description    = each.value.description
  topic_name     = each.value.topic_name

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "notifications-subscriptions" {
  source   = "./modules/managementservices/notification-subscription"
  for_each = var.notifications_subscriptions != null ? var.notifications_subscriptions : {}

  depends_on     = [module.notifications-topics]
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  endpoint       = each.value.endpoint
  protocol       = each.value.protocol
  topic_id       = length(regexall("ocid1.onstopic.oc*", each.value.topic_id)) > 0 ? each.value.topic_id : merge(module.notifications-topics.*...)[each.value.topic_id]["topic_tf_id"]
  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "notifications-topics" {
  value = [ for k,v in merge(module.notifications-topics.*...) : v.topic_tf_id ]
}
*/

####################################
## Module Block - Service Connector
## Create Service Connectors
####################################

module "service-connectors" {
  source = "./modules/managementservices/service-connector"

  for_each = var.service_connectors

  compartment_id            = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null
  logs_compartment_id       = var.tenancy_ocid
  source_monitoring_details = each.value.source_details.source_kind == "monitoring" ? { for k, v in each.value.source_details.source_monitoring_details : lookup(var.compartment_ocids, k, "not_found") => v } : {}
  target_monitoring_details = each.value.target_details.target_kind == "monitoring" ? { for k, v in each.value.target_details.target_monitoring_details : lookup(var.compartment_ocids, k, "not_found") => v } : {}
  log_group_names           = each.value.source_details.source_kind == "logging" ? flatten([for key in each.value.source_details.source_log_group_names : join("@", tolist([lookup(var.compartment_ocids, split("@", key)[0], "null"), split("@", key)[1], split("@", key)[2]]))]) : []
  display_name              = each.value.display_name
  description               = each.value.description
  source_kind               = each.value.source_details.source_kind
  target_kind               = each.value.target_details.target_kind

  stream_id          = each.value.target_details.target_kind == "streaming" ? { for k, v in each.value.target_details.target_stream_name : lookup(var.compartment_ocids, k, "null") => v } : {}
  source_stream_id   = each.value.source_details.source_kind == "streaming" ? { for k, v in each.value.source_details.source_stream_name : lookup(var.compartment_ocids, k, "null") => v } : {}
  bucket_name        = each.value.target_details.target_kind == "objectStorage" ? each.value.target_details.target_bucket_name : ""
  object_name_prefix = each.value.target_details.target_kind == "objectStorage" ? each.value.target_details.target_object_name_prefix : ""

  topic_id                     = each.value.target_details.target_kind == "notifications" ? { for k, v in each.value.target_details.target_topic_name : lookup(var.compartment_ocids, k, "null") => v } : {}
  enable_formatted_messaging   = each.value.target_details.target_kind == "notifications" ? each.value.target_details.enable_formatted_messaging : false
  destination_log_group_id     = each.value.target_details.target_kind == "loggingAnalytics" ? { for k, v in each.value.target_details.target_log_group_name : lookup(var.compartment_ocids, k, "null") => v } : {}
  target_log_source_identifier = each.value.source_details.source_kind == "streaming" && each.value.target_details.target_kind == "loggingAnalytics" ? each.value.target_details.target_log_source_identifier : ""

  function_details = each.value.target_details.target_kind == "functions" ? flatten([for key in each.value.target_details.target_function_details : join("@", tolist([lookup(var.compartment_ocids, split("@", key)[0], "null"), split("@", key)[1], split("@", key)[2]]))]) : []
  #Optional
  defined_tags  = try(each.value["defined_tags"], {})
  freeform_tags = try(each.value["freeform_tags"], {})
}