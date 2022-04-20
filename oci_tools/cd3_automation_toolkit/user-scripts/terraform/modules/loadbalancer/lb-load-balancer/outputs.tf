// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Load Balancer
# Create Load Balancer
############################

output "load_balancer_tf_id" {
  description = "Load Balancer ocid"
  value       = oci_load_balancer_load_balancer.load_balancer.id
}
