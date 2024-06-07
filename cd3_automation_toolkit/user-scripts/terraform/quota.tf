// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#######################################
# Module Block - QUOTA POLICIES
# Create Quota policies
#######################################

module "quota_policies" {
  source                          = "./modules/governance/quota-policy"
  for_each                        = var.quota_policies
  tenancy_ocid                    = var.tenancy_ocid
  quota_description               = each.value.quota_description
  quota_name                      = each.value.quota_name
  quota_statements                = each.value.quota_statements
  defined_tags                    = each.value.defined_tags
  freeform_tags                   = each.value.freeform_tags
}
