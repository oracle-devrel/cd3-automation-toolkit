// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Network
# Create Network Security Groups
#############################

output "nsg_id" {
	value = zipmap(oci_core_network_security_group.network_security_group.*.display_name,oci_core_network_security_group.network_security_group.*.id)
}