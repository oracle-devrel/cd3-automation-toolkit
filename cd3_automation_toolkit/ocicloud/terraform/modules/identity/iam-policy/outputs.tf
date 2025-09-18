# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Identity
# Create Policies
############################

output "policies_tf_id" {
  value = oci_identity_policy.policy.id
}
