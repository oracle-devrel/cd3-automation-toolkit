# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Resource Block - Network Load Balancer
# Create Network Load Balancer Backend Set
#######################################

output "nlb_backend_set_tf_id" {
  description = "Load Balancer Backend Set ocid"
  value       = oci_network_load_balancer_backend_set.backend_set.id
}

output "nlb_backend_set_tf_name" {
  description = "Load Balancer Backend Set Name"
  value       = oci_network_load_balancer_backend_set.backend_set.name
}