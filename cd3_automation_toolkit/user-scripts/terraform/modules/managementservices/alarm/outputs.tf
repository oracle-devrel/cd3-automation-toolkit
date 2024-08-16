# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - ManagementServices
# Create Alarms
############################

output "alarm_tf_id" {
  description = "Alarm OCID"
  value       = oci_monitoring_alarm.alarm.id
}