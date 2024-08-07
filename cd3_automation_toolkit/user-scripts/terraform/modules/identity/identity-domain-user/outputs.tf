// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Users
############################

output "user_id_map" {
  description = "user ocid"
  value       = zipmap(oci_identity_domains_user.user.*.user_name, oci_identity_domains_user.user.*.id)
}

