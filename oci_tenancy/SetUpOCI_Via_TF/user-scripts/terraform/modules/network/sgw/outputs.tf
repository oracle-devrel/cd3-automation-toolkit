// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Networking
# Create Service Gateway
############################

output "sgw_id" {
	value = zipmap(oci_core_service_gateway.service_gateway.*.display_name, oci_core_service_gateway.service_gateway.*.id)
}