# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Governance
# Create Tag Defaults
############################

output "quota_tf_id" {
  description = "Quota ocid"
  value       = oci_limits_quota.quota.id
}
