// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Internet Gateway
############################

output "igw_id" {
	value = zipmap(oci_core_internet_gateway.internet_gateway.*.display_name, oci_core_internet_gateway.internet_gateway.*.id)
}

output "igw_tf_id" {
	value =  oci_core_internet_gateway.internet_gateway.*.id
}