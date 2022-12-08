// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Network
# Create Network Security Groups
#############################

output "nsg_tf_id" {
  value = oci_core_network_security_group.network_security_group.id
}