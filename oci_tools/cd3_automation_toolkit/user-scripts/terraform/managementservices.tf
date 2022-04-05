// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - ManagementServices
# Create Alarms
############################

module "alarms" {
  source   = "./modules/managementservices/alarm"

  depends_on = [module.notifications-topics]
  for_each = var.alarms != null ? var.alarms : {}

  alarm_name                   = each.value.alarm_name
  compartment_name             = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
  destinations                 = [for tn in each.value.destinations : (length(regexall("ocid1.onstopic.oc1*", tn)) > 0 ? tn : merge(module.notifications-topics.*...)[tn]["topic_tf_id"])]
  is_enabled                   = each.value.is_enabled
  metric_compartment_name      = each.value.metric_compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.metric_compartment_name)) > 0 ? each.value.metric_compartment_name : var.compartment_ocids[each.value.metric_compartment_name]) : null
  namespace                    = each.value.namespace
  query                        = each.value.query
  severity                     = each.value.severity
  body                         = each.value.body
  message_format               = each.value.message_format
  trigger_delay_minutes        = each.value.trigger_delay_minutes == null ? "" : each.value.trigger_delay_minutes
  repeat_notification_duration = each.value.repeat_notification_duration == null ? "" : each.value.repeat_notification_duration


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
  source   = "./modules/managementservices/event"
  depends_on = [module.notifications-topics]
  for_each = var.events != null ? var.events : {}

  event_name       = each.value.event_name
  compartment_name = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
  is_enabled       = each.value.is_enabled
  description      = (each.value.description != "" && each.value.description != null) ? each.value.description : null
  condition        = each.value.condition
  actions          = var.events
  key_name         = each.key
  topic_name       = merge(module.notifications-topics.*...)

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

  compartment_name = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
  description      = each.value.description
  topic_name       = each.value.topic_name

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "notifications-subscriptions" {
  source   = "./modules/managementservices/notification-subscription"
  for_each = var.notifications_subscriptions != null ? var.notifications_subscriptions : {}

  depends_on        = [module.notifications-topics]
  compartment_name  = each.value.compartment_name != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_name)) > 0 ? each.value.compartment_name : var.compartment_ocids[each.value.compartment_name]) : null
  endpoint          = each.value.endpoint
  protocol          = each.value.protocol
  topic_name        = length(regexall("ocid1.onstopic.oc1*", each.value.topic_name)) > 0 ? each.value.topic_name : merge(module.notifications-topics.*...)[each.value.topic_name]["topic_tf_id"]
  subscription_name = each.value.subscription_name
  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "notifications-topics" {
  value = [ for k,v in merge(module.notifications-topics.*...) : v.topic_tf_id ]
}
*/