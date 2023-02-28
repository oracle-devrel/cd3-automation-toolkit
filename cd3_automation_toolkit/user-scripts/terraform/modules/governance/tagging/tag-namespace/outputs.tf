// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Governance
# Create Namespaces
############################

output "namespace_tf_id" {
  description = "Namespace ocid"
  value       = oci_identity_tag_namespace.tag_namespace.id
}
