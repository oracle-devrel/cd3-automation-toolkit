// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - ManagementServices
# Create Alarms
############################

/*
output "group_id_map" {
  description = "Group ocid"
  value = zipmap(oci_identity_group.group.*.name,oci_identity_group.group.*.id)
}


output "group_name" {
  description = "Group name"
  value = var.group_name
}

output "name_ocid" {
  value       = zipmap(oci_identity_group.this[*].name, oci_identity_group.this[*].id)
  description = "group name and associated OCID"
}
*/