// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Module Block - Governance
# Create Budgets and Rule Alerts
############################

module "budgets" {
  source   = "./modules/governance/billing/budget"
  for_each = var.budgets != null ? var.budgets : {}

  #Required
  amount         = each.value.amount
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  reset_period   = each.value.reset_period != null ? each.value.reset_period : "MONTHLY"

  #Optional
  budget_processing_period_start_offset = each.value.budget_processing_period_start_offset
  description                           = each.value.description
  display_name                          = each.value.display_name
  defined_tags                          = each.value.defined_tags
  freeform_tags                         = each.value.freeform_tags
  processing_period_type                = each.value.processing_period_type
  #target_compartment_id = each.value.target_compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.target_compartment_id)) > 0 ? each.value.target_compartment_id : var.compartment_ocids[each.value.target_compartment_id]) : null
  target_type = each.value.target_type
  targets     = each.value.targets != null ? [var.compartment_ocids[flatten([for targets in each.value.targets : targets])[0]]] : []

}

module "budget-alert-rules" {
  source   = "./modules/governance/billing/budget-alert-rule"
  for_each = var.budget_alert_rules != null ? var.budget_alert_rules : {}

  #Required
  budget_id      = each.value.budget_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.budget_id)) > 0 ? each.value.budget_id : merge(module.budgets.*...)[each.value.budget_id]["budget_tf_id"]) : null
  threshold      = each.value.threshold
  threshold_type = each.value.threshold_type
  type           = each.value.type

  #Optional
  description   = each.value.description
  display_name  = each.value.display_name
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
  message       = each.value.message
  recipients    = each.value.recipients
}