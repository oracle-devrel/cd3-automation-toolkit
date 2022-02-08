// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Route Table
############################

output "route_id" {
	value = zipmap(oci_core_route_table.route_table.*.display_name,oci_core_route_table.route_table.*.id)
}

output "route_subnet_id" {
	value = oci_core_route_table.route_table.*.id
}