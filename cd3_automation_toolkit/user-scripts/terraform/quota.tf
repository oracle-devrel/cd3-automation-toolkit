# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#######################################
# Module Block - QUOTA POLICIES
# Create Quota policies
#######################################

module "quota_policies" {
  source            = "./modules/governance/quota-policy"
  for_each          = var.quota_policies
  tenancy_ocid      = var.tenancy_ocid
  quota_description = each.value.quota_description
  quota_name        = each.value.quota_name
  quota_statements  = each.value.quota_statements
  defined_tags      = each.value.defined_tags
  freeform_tags     = each.value.freeform_tags
}
