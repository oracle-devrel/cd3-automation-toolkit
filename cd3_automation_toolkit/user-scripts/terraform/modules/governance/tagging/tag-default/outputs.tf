# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Governance
# Create Tag Defaults
############################

output "tag_default_tf_id" {
  description = "Tag Default ocid"
  value       = oci_identity_tag_default.tag_default.id
}
