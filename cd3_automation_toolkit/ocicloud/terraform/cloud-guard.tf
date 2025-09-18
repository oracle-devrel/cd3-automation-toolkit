# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Security
# Create Cloud Guard Configuration and Cloud Guard Targets
############################

module "cloud-guard-configurations" {
  source   = "./modules/security/cloud-guard-configuration"
  for_each = var.cloud_guard_configs != null ? var.cloud_guard_configs : {}

  #Required
  compartment_id   = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  reporting_region = each.value.reporting_region
  status           = each.value.status

  #Optional
  self_manage_resources = each.value.self_manage_resources
}

module "cloud-guard-targets" {
  source   = "./modules/security/cloud-guard-target"
  for_each = var.cloud_guard_targets != null ? var.cloud_guard_targets : {}

  depends_on = [module.cloud-guard-configurations]
  #Required
  tenancy_ocid         = var.tenancy_ocid
  compartment_id       = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  display_name         = each.value.display_name
  target_resource_id   = each.value.target_resource_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.target_resource_id)) > 0 ? each.value.target_resource_id : var.compartment_ocids[each.value.target_resource_id]) : each.value.target_resource_id
  target_resource_type = each.value.target_resource_type != null ? each.value.target_resource_type : "COMPARTMENT"
  prefix               = each.value.prefix

  #Optional
  defined_tags             = each.value.defined_tags
  description              = each.value.description
  freeform_tags            = each.value.freeform_tags
  state                    = each.value.state
  target_detector_recipes  = each.value.target_detector_recipes
  target_responder_recipes = each.value.target_responder_recipes
}
