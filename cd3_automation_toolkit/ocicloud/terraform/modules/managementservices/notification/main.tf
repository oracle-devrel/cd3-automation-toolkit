# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - ManagementServices
# Create Notifications_Topics
############################

resource "oci_ons_notification_topic" "topic" {

  #Required
  compartment_id = var.compartment_id
  name           = var.topic_name
  description    = var.description

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}

resource "oci_ons_subscription" "subscription" {

  count = length(var.subscriptions)
  #Required
  compartment_id = var.compartment_id
  endpoint       = var.subscriptions[count.index].endpoint
  protocol       = var.subscriptions[count.index].protocol
  topic_id       = oci_ons_notification_topic.topic.id

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags
 lifecycle {
   ignore_changes = [defined_tags,freeform_tags]
 }
}