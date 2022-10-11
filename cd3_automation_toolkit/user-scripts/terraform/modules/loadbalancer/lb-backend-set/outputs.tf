// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Load Balancer
# Create Load Balancer Backend Set
############################

output "backend_set_tf_id" {
  description = "Load Balancer Backend Set ocid"
  value       = oci_load_balancer_backend_set.backend_set.id
}

output "backend_set_tf_name" {
  description = "Load Balancer Backend Set Name"
  value       = oci_load_balancer_backend_set.backend_set.name
}