# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Governance
# Create Tag Key
############################

output "tag_key_tf_id" {
  description = "Tag Key ocid"
  value       = oci_identity_tag.tag.id
}
