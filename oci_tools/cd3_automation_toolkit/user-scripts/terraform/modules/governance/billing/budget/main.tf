// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Governance
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
  #target_compartment_id  = var.target_compartment_id
  target_type = var.target_type
  targets     = var.targets

}
