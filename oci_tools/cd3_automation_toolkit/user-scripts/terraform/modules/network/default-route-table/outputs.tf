// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Default Route Table
############################

output "default_route_table_tf_id" {
  value = oci_core_default_route_table.default_route_table.id
}