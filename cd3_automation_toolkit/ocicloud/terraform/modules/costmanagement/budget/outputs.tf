# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Outputs Block - Cost Management
## Create Budget
################################

output "budget_tf_id" {
  value = oci_budget_budget.budget.id
}