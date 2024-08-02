# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Governance
# Create Namespaces
############################

output "namespace_tf_id" {
  description = "Namespace ocid"
  value       = oci_identity_tag_namespace.tag_namespace.id
}
