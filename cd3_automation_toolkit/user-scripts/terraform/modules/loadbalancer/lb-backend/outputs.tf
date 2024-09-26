# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Load Balancer
# Create Load Balancer Backend
############################

output "backend_tf_id" {
  description = "Load Balancer Backend ocid"
  value       = oci_load_balancer_backend.backend.id
}
