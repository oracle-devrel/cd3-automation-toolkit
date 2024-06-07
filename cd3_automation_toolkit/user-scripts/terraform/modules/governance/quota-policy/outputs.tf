// Copyright (c) 2024, Oracle and/or its affiliates.

############################
# Output Block - Governance
# Create Tag Defaults
############################

output "quota_tf_id" {
  description = "Quota ocid"
  value       = oci_limits_quota.quota.id
}
