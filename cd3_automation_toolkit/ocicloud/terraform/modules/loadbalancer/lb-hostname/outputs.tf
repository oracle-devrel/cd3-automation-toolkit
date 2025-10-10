# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Load Balancer
# Create Load Balancer Hostname
############################

output "hostname_tf_id" {
  description = "Load Balancer Hostname ocid"
  value       = oci_load_balancer_hostname.hostname.id
}

output "hostname_tf_name" {
  description = "Load Balancer Hostname Name"
  value       = oci_load_balancer_hostname.hostname.name
}
