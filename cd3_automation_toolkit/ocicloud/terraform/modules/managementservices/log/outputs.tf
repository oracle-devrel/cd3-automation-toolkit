# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - ManagementServices
# Create Log
############################

output "log_tf_id" {
  description = "Log OCID"
  value       = oci_logging_log.log.id
}