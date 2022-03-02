// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create NAT Gateway
############################

output "ngw_tf_id" {
  value = oci_core_nat_gateway.nat_gateway.id
}