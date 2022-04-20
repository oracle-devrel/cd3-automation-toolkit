// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Load Balancer
# Create Load Balancer Backend
############################

output "backend_tf_id" {
  description = "Load Balancer Backend ocid"
  value       = oci_load_balancer_backend.backend.id
}
