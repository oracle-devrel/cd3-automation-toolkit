// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - ManagementServices
# Create Notifications_Subscriptions
############################

resource "oci_ons_subscription" "subscription" {
  count = var.subscription_name != null ? 1 : 0
  #Required
  compartment_id = var.compartment_name
  endpoint = var.endpoint
  protocol = var.protocol
  topic_id = var.topic_name

  #Optional
  defined_tags = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"],defined_tags["Oracle-Tags.CreatedBy"],freeform_tags]
    }
}
