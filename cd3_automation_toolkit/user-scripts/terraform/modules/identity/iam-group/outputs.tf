// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Groups
############################

output "group_id_map" {
  description = "Group ocid"
  value       = zipmap(oci_identity_group.group.*.name, oci_identity_group.group.*.id)
}

output "dynamic_group_id_map" {
  description = "Dynamic Group ocid"
  value       = zipmap(oci_identity_dynamic_group.dynamic_group.*.name, oci_identity_dynamic_group.dynamic_group.*.id)
}
