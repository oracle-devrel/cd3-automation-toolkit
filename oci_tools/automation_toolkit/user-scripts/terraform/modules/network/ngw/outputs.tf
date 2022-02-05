// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create NAT Gateway
############################

output "ngw_id" {
	value = zipmap(oci_core_nat_gateway.nat_gateway.*.display_name, oci_core_nat_gateway.nat_gateway.*.id)
}

output "ngw_tf_id" {
	value =  oci_core_nat_gateway.nat_gateway.*.id
}