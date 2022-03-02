// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Logging
# Create Log Groups
#############################

output "log_group_tf_id" {
  value = oci_logging_log_group.log_group.id
}