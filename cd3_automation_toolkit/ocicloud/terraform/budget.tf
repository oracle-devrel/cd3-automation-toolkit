# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Cost Management
# Create Budgets and Rule Alerts
############################

#locals {
#	comp_ocids = {for key, val in var.budgets : key => [
#    var.compartment_ocids[flatten([for targets in val.targets : targets])[0]]
#      ] if val.target_type == "COMPARTMENT" }
#}



module "budget-alert-rules" {
  source   = "./modules/costmanagement/budget-alert-rule"
  for_each = var.budget_alert_rules

  #Required
  budget_id      = length(regexall("ocid1.budget.oc*", each.value.budget_id)) > 0 ? each.value.budget_id : merge(module.budgets.*...)[each.value.budget_id]["budget_tf_id"]
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

module "budgets" {
  source   = "./modules/costmanagement/budget"
  for_each = var.budgets

  #Required
  amount         = each.value.amount
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid

  reset_period = each.value.reset_period != null ? each.value.reset_period : "MONTHLY"

  #Optional
  budget_processing_period_start_offset = each.value.budget_processing_period_start_offset
  description                           = each.value.description
  display_name                          = each.value.display_name
  defined_tags                          = each.value.defined_tags
  freeform_tags                         = each.value.freeform_tags
  processing_period_type                = each.value.processing_period_type
  budget_start_date                     = each.value.processing_period_type == "SINGLE_USE" ? each.value.budget_start_date : null
  budget_end_date                       = each.value.processing_period_type == "SINGLE_USE" ? each.value.budget_end_date : null

  #target_compartment_id = each.value.target_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.target_compartment_id)) > 0 ? each.value.target_compartment_id : var.compartment_ocids[each.value.target_compartment_id]) : null

  target_type = each.value.target_type
  #targets = each.value.targets

  targets = each.value.target_type == "COMPARTMENT" ? (length(regexall("ocid1.compartment.oc*", each.value.targets[0])) > 0 ? each.value.targets : [var.compartment_ocids[each.value.targets[0]]]) : each.value.targets

}