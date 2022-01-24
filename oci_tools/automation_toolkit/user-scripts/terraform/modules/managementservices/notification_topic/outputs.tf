// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Notifications_Topics
############################

output "topic_id" {
  description = "Topic ocid"
  value = zipmap(oci_ons_notification_topic.topic.*.name,oci_ons_notification_topic.topic.*.id)
}