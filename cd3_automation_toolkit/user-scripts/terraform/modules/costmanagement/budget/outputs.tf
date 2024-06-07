// Copyright (c) 2024, Oracle and/or its affiliates.

################################
## Outputs Block - Cost Management
## Create Budget
################################

output "budget_tf_id" {
  value = oci_budget_budget.budget.id
}