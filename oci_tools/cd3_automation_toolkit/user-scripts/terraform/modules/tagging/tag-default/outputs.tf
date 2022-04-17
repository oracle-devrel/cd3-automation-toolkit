// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Governance
# Create Tag Defaults
############################

output "tag_default_tf_id" {
  description = "Tag Default ocid"
  value       = oci_identity_tag_default.tag_default.id
}
