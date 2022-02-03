// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Fetch VCNs
############################

output "vcns" {
  value = zipmap(data.oci_core_vcns.vcns.virtual_networks.*.display_name,data.oci_core_vcns.vcns.virtual_networks.*.id)
}
