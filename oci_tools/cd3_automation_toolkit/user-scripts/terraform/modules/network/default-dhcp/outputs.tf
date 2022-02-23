// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Default DHCP Options
############################

output "default_dhcp_id" {
	value = zipmap(oci_core_default_dhcp_options.default_dhcp_option.*.display_name,oci_core_default_dhcp_options.default_dhcp_option.*.id)
}

output "default_dhcp_subnet_id" {
	value = oci_core_default_dhcp_options.default_dhcp_option.*.id
}