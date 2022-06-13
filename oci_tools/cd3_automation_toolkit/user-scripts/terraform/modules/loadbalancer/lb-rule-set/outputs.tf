// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Load Balancer
# Create Load Balancer Rule Set
############################

output "rule_set_tf_id" {
  description = "Load Balancer Rule Set ocid"
  value       = oci_load_balancer_rule_set.rule_set.id
}

output "rule_set_tf_name" {
  description = "Load Balancer Rule Set Name"
  value       = oci_load_balancer_rule_set.rule_set.name
}

