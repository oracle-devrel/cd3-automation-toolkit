# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
################################
## Resource Block - Cost Management
## Create Budget
################################

resource "oci_budget_budget" "budget" {
  #Required
  amount         = var.amount
  compartment_id = var.compartment_id
  reset_period   = var.reset_period

  #Optional
  budget_processing_period_start_offset = var.budget_processing_period_start_offset
  defined_tags                          = var.defined_tags
  description                           = var.description
  display_name                          = var.display_name
  freeform_tags                         = var.freeform_tags
  processing_period_type                = var.processing_period_type
  #start_date                            = var.budget_start_date != null ?join("T",[var.budget_start_date,"00:00:00.00Z"]):null
  #end_date                              = var.budget_end_date != null ?join("T",[var.budget_end_date,"23:59:59.999Z"]):null
  start_date                            = var.budget_start_date != null ?"${var.budget_start_date}T00:00:00.001-00:00":null
  end_date                              = var.budget_end_date != null ?"${var.budget_end_date}T23:59:59.001-00:00":null
  target_type = var.target_type
  targets     = var.targets
  lifecycle {
    ignore_changes = [start_date,end_date]
  }


}
