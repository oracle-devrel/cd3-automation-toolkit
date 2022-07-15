// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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