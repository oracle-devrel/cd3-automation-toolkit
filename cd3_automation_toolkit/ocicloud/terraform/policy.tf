# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#


############################
# Module Block - Identity
# Create Policies
############################

module "iam-policies" {
  source   = "./modules/identity/iam-policy"
  for_each = var.policies

  #depends_on            = [module.iam-groups]
  tenancy_ocid          = var.tenancy_ocid
  policy_name           = each.value.name
  policy_compartment_id = each.value.compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  policy_description    = each.value.policy_description
  policy_statements     = each.value.policy_statements

  #Optional
  defined_tags        = each.value.defined_tags
  freeform_tags       = each.value.freeform_tags
  policy_version_date = each.value.policy_version_date
}
