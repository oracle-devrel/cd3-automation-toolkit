// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Custom DHCP Options
############################

output "custom_dhcp_id" {
	value = zipmap(oci_core_dhcp_options.custom_dhcp_option.*.display_name,oci_core_dhcp_options.custom_dhcp_option.*.id)
}

