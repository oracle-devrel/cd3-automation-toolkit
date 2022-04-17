// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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