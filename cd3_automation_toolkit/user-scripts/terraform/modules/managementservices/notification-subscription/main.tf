# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
