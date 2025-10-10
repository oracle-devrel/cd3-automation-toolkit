# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Output Block - Load Balancer
# Create Load Balancer Cipher Suite
############################

output "cipher_suite_tf_id" {
  description = "Load Balancer Cipher Suite ocid"
  value       = oci_load_balancer_ssl_cipher_suite.ssl_cipher_suite.id
}

output "cipher_suite_tf_name" {
  description = "Load Balancer Cipher Suite Name"
  value       = oci_load_balancer_ssl_cipher_suite.ssl_cipher_suite.name
}