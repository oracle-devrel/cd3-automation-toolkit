// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Fetch Subnets
############################

output "subnets" {
  value = zipmap(data.oci_core_subnets.subnets.virtual_networks.*.display_name,data.oci_core_subnets.subnets.virtual_networks.*.id)
}
