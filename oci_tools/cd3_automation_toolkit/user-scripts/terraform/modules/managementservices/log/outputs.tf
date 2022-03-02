// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Log
############################

output "log_tf_id" {
  description = "Log OCID"
  value       = oci_logging_log.log.id
}