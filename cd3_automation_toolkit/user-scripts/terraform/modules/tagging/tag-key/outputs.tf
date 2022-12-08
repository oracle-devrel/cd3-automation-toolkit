// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Governance
# Create Tag Key
############################

output "tag_key_tf_id" {
  description = "Tag Key ocid"
  value       = oci_identity_tag.tag.id
}
