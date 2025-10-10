# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - ManagementServices
# Create Notifications_Topics
############################

output "topic_tf_id" {
  description = "Topic OCID"
  value       = oci_ons_notification_topic.topic.id
}