// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Route Table
############################

output "route_table_ids" {
  value = oci_core_route_table.route_table.id
}