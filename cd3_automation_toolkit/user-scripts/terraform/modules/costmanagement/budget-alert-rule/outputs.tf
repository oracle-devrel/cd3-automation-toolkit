// Copyright (c) 2024, Oracle and/or its affiliates.

################################
## Outputs Block - Cost Management
## Create Budget Alert Rule
################################

output "budget_alert_rule_tf_id" {
  value = oci_budget_alert_rule.alert_rule.id
}