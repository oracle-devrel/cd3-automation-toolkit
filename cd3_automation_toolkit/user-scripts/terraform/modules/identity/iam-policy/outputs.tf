// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Policies
############################

output "policies_tf_id" {
  value = oci_identity_policy.policy.id
}
