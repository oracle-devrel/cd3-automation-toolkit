// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Networking
# Create Security List
############################

output "seclist_id" {
	value = zipmap(oci_core_security_list.security_list.*.display_name,oci_core_security_list.security_list.*.id) 
}