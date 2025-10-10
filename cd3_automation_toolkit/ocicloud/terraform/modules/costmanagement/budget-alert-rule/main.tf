# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Cost Management
## Create Budget Alert Rule
################################

resource "oci_budget_alert_rule" "alert_rule" {
  #Required
  budget_id      = var.budget_id
  threshold      = var.threshold
  threshold_type = var.threshold_type
  type           = var.type

  #Optional
  defined_tags  = var.defined_tags
  description   = var.description
  display_name  = var.display_name
  freeform_tags = var.freeform_tags
  message       = var.message
  recipients    = var.recipients

}
