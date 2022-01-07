// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Policies
############################

output "policies_id_map" {
  value = zipmap(oci_identity_policy.policy.*.name,oci_identity_policy.policy.*.id)
}
