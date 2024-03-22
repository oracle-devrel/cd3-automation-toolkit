// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Governance
## Create Budget
################################

output "budget_tf_id" {
  value = oci_budget_budget.budget.id
}