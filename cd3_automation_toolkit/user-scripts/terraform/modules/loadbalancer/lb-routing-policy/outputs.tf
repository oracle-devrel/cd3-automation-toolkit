// Copyright (c) 2024, 2025, Oracle and/or its affiliates.

#####################################
# Output Block - Load Balancer
# Create Load Balancer Routing Policy
#####################################

output "id" {
  description = "The OCID of the load balancer routing policy."
  value       = oci_load_balancer_load_balancer_routing_policy.load_balancer_routing_policy.id
}
