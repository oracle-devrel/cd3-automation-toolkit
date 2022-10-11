// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Output Block - Networking
# Create Network Security Groups
#############################

output "nsg_rule_tf_id" {
  value = oci_core_network_security_group_security_rule.nsg_rule.id
}
