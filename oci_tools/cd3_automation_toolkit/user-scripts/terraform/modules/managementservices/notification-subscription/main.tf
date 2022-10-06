// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - ManagementServices
# Create Notifications_Subscriptions
############################

resource "oci_ons_subscription" "subscription" {

  #Required
  compartment_id = var.compartment_id
  endpoint       = var.endpoint
  protocol       = var.protocol
  topic_id       = var.topic_id

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}
