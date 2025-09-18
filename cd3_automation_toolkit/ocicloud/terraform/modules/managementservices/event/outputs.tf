# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - ManagementServices
# Create Events
############################

output "event_tf_id" {
  description = "Event OCID"
  value       = oci_events_rule.event.id
}