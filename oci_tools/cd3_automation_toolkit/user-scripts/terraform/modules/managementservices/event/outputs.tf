// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Events
############################

output "event_tf_id" {
  description = "Event OCID"
  value       = oci_events_rule.event.id
}