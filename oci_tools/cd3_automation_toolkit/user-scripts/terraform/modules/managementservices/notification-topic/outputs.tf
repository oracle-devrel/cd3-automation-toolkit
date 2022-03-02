// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Notifications_Topics
############################

output "topic_tf_id" {
  description = "Topic OCID"
  value       = oci_ons_notification_topic.topic.id
}