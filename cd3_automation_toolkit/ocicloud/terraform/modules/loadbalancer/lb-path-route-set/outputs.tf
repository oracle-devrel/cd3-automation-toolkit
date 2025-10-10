# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Load Balancer
# Create Load Balancer Path Route Set
############################

output "path_route_set_tf_id" {
  description = "Load Balancer Path Route Set ocid"
  value       = oci_load_balancer_path_route_set.path_route_set.id
}

output "path_route_set_tf_name" {
  description = "Load Balancer Path Route Set Name"
  value       = oci_load_balancer_path_route_set.path_route_set.name
}
