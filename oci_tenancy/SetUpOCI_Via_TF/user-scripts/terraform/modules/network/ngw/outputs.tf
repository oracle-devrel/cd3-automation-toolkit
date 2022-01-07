// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Networking
# Create NAT Gateway
############################

output "ngw_id" {
	value = zipmap(oci_core_nat_gateway.nat_gateway.*.display_name, oci_core_nat_gateway.nat_gateway.*.id)
}