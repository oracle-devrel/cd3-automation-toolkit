// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Groups
############################
output "group_id_map" {
  description = "Group ocid"
  value       = zipmap(oci_identity_domains_group.group.*.display_name, oci_identity_domains_group.group.*.id)
}

output "dynamic_group_id_map" {
  description = "Dynamic Group ocid"
  value       = zipmap(oci_identity_domains_dynamic_resource_group.dynamic_group.*.display_name, oci_identity_domains_dynamic_resource_group.dynamic_group.*.id)
}



