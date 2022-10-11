// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Alarms
############################

output "alarm_tf_id" {
  description = "Alarm OCID"
  value       = oci_monitoring_alarm.alarm.id
}