// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Output Block - Network
# Create DRG Route Rule
############################

output "drg_route_rule_tf_id" {
  value = oci_core_drg_route_table_route_rule.drg_route_rule.id
}
