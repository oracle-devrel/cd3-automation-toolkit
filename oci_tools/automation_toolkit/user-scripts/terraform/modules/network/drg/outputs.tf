// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Networking
# Create Dynamic Routing Gateway
############################

output "drg_id" {
	value = zipmap(oci_core_drg.drg.*.display_name, oci_core_drg.drg.*.id)
}
