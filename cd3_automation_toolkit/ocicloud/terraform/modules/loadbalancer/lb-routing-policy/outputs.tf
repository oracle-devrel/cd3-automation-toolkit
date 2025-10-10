# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#####################################
# Output Block - Load Balancer
# Create Load Balancer Routing Policy
#####################################

output "id" {
  description = "The OCID of the load balancer routing policy."
  value       = oci_load_balancer_load_balancer_routing_policy.load_balancer_routing_policy.id
}
