# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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



