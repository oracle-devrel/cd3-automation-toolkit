// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
