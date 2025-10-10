# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Load Balancer
# Create Load Balancer Certificate
############################

output "certificate_tf_id" {
  description = "Load Balancer Certificate ocid"
  value       = oci_load_balancer_certificate.certificate.id
}

output "certificate_tf_name" {
  description = "Load Balancer Certificate Name"
  value       = oci_load_balancer_certificate.certificate.certificate_name
}