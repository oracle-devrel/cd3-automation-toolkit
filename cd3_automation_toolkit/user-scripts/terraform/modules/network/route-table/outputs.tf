// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Route Table
############################

output "route_table_ids" {
  value = one(concat(oci_core_route_table.route_table.*.id,oci_core_default_route_table.default_route_table.*.id))
  #value = concat(oci_core_route_table.route_table.*.id,oci_core_default_route_table.default_route_table.*.id)[0]
}

