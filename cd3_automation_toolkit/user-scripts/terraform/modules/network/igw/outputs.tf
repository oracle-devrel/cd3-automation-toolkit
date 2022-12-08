// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create Internet Gateway
############################

output "igw_tf_id" {
  value = oci_core_internet_gateway.internet_gateway.id
}