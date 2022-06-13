// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Load Balancer
# Create Load Balancer Listener
############################

output "listener_tf_id" {
  description = "Load Balancer Listener ocid"
  value       = oci_load_balancer_listener.listener.id
}
