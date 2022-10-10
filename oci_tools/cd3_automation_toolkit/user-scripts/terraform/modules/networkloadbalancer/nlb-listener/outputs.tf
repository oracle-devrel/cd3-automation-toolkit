// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Output Block - Network Load Balancer
# Create Network Load Balancer Listener
#######################################

output "nlb_listener_tf_id" {
  description = "Network Load Balancer Listener ocid"
  value       = oci_network_load_balancer_listener.listener.id
}
