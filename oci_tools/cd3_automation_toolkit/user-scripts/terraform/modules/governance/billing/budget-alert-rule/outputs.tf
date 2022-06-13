// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Governance
## Create Budget Alert Rule
################################

output "budget_alert_rule_tf_id" {
  value = oci_budget_alert_rule.alert_rule.id
}