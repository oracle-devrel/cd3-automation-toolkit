// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
