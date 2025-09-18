# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Output Block - Logging
# Create Log Groups
#############################

output "log_group_tf_id" {
  value = oci_logging_log_group.log_group.id
}