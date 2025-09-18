# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Identity
# Create Network Source
############################

output "networksource_id_map" {
  description = "networksource ocid"
  value       = zipmap(oci_identity_network_source.network_source.*.name, oci_identity_network_source.network_source.*.id)
}
