# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Output Block - Network Load Balancer
# Create Network Load Balancer Listener
#######################################

output "nlb_listener_tf_id" {
  description = "Network Load Balancer Listener ocid"
  value       = oci_network_load_balancer_listener.listener.id
}
