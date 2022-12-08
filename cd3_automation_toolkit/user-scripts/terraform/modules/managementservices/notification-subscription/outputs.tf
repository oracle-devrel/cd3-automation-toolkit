// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Notifications_Subscriptions
############################

output "topic_subscription_tf_id" {
  description = "Topic Subscription OCID"
  value       = oci_ons_subscription.subscription.id
}