// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Output Block - Network Load Balancer
# Create Network Load Balancer
#######################################

output "network_load_balancer_tf_id" {
  description = "Network Load Balancer ocid"
  value       = oci_network_load_balancer_network_load_balancer.network_load_balancer.id
}