// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Default Security List
############################

output "default_seclist_id" {
	value = zipmap(oci_core_default_security_list.default_security_list.*.display_name,oci_core_default_security_list.default_security_list.*.id)
}