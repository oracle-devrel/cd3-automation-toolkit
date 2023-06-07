// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Identity
# Create Network Source
############################

output "networksource_id_map" {
  description = "networksource ocid"
  value       = zipmap(oci_identity_network_source.network_source.*.name, oci_identity_network_source.network_source.*.id)
}
