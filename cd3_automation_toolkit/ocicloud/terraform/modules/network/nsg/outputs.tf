# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Output Block - Network
# Create Network Security Groups
#############################

output "nsg_tf_id" {
  value = oci_core_network_security_group.network_security_group.id
}