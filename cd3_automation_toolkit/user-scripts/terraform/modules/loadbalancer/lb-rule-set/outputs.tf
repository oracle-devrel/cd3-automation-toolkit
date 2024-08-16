# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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

