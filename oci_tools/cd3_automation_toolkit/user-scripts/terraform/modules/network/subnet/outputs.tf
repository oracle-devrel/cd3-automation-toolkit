// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Network
# Create Subnets
#############################

output "subnet_tf_id" {
  value = oci_core_subnet.subnet.id
}