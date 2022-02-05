// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Dynamic Routing Gateway
############################

output "drg_id" {
	value = zipmap(oci_core_drg.drg.*.display_name, oci_core_drg.drg.*.id)
}

output "drg_tf_id" {
	value = oci_core_drg.drg.*.id
}