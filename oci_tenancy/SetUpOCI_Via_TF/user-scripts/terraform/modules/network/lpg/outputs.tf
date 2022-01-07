// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Networking
# Create Local Peering Gateway
############################

output "lpg_id" {
	value = zipmap(oci_core_local_peering_gateway.local_peering_gateway.*.display_name, oci_core_local_peering_gateway.local_peering_gateway.*.id)
}