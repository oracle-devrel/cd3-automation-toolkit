# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#


############################
# Module Block - Identity
# Create Users
############################

module "iam-users" {
  source = "./modules/identity/iam-user"
  #depends_on       = [module.iam-groups]
  for_each             = var.users
  user_name            = each.value.name
  user_description     = each.value.description
  user_email           = each.value.email
  tenancy_ocid         = var.tenancy_ocid
  enabled_capabilities = each.value.enabled_capabilities != null ? each.value.enabled_capabilities : null

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}




/*
output "group_id_map" {
  value = [ for k,v in merge(module.iam-groups.*...) : v.group_id_map]
}


output "dynamic_group_id_map" {
  value = [ for k,v in merge(module.iam-groups.*...) : v.dynamic_group_id_map]
}
*/

############################
# Module Block - Identity
# Create Identity Domain Groups
############################
locals {
  # get all the domains used for users
  users_unique_idcs_endpoints = {
    for k, v in var.identity_domain_users :
    v.idcs_endpoint => {
      idcs_endpoint         = v.idcs_endpoint
      domain_compartment_id = v.domain_compartment_id
    }...
  }
  # get all the domains used for groups
  groups_unique_idcs_endpoints = {
    for k, v in var.identity_domain_groups :
    v.idcs_endpoint => {
      idcs_endpoint         = v.idcs_endpoint
      domain_compartment_id = v.domain_compartment_id
    }...
  }
  # get unique domains used across users and groups
  domains_distinct = { for k, v in merge(local.groups_unique_idcs_endpoints, local.users_unique_idcs_endpoints) : k => distinct(v)[0]... }

  # users in each domain used in groups
  domain_users_map = {
    for k, v in local.domains_distinct :
    k => {
      for user in data.oci_identity_domains_users.users[k].users :
      user.user_name => user.id
    } if contains(keys(local.groups_unique_idcs_endpoints), k)
  }

}
# output "domain_distinct" {
#   value = local.domains_distinct
# }
# output "groups_unique_idcs_endpoints" {
#   value = local.groups_unique_idcs_endpoints
# }

# domain data for unique domin used across users and groups
data "oci_identity_domains" "iam_domains" {
  for_each = local.domains_distinct
  # Required
  compartment_id = var.compartment_ocids[each.value[0].domain_compartment_id]
  # Optional
  display_name = each.key
}

# user data for each used domain
data "oci_identity_domains_users" "users" {
  for_each      = { for k, v in local.domains_distinct : k => v if contains(keys(local.groups_unique_idcs_endpoints), k) }
  idcs_endpoint = data.oci_identity_domains.iam_domains[each.value[0].idcs_endpoint].domains[0].url
}

# output "user_map" {
#   value = local.domain_users_map
# }


############################
# Module Block - Identity
# Create Identity Domain Users
############################

module "users" {
  source = "./modules/identity/identity-domain-user"
  #depends_on       = [module.iam-groups]
  for_each             = var.identity_domain_users
  user_name            = each.value.user_name
  family_name          = each.value.name.family_name
  given_name           = each.value.name.given_name
  middle_name          = each.value.name.middle_name
  honorific_prefix     = each.value.name.honorific_prefix
  display_name         = each.value.display_name
  identity_domain      = data.oci_identity_domains.iam_domains[each.value.idcs_endpoint].domains[0]
  compartment_id       = each.value.domain_compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.domain_compartment_id)) > 0 ? each.value.domain_compartment_id : var.compartment_ocids[each.value.domain_compartment_id]) : var.tenancy_ocid
  description          = each.value.description
  email                = each.value.email
  recovery_email       = each.value.recovery_email
  tenancy_ocid         = var.tenancy_ocid
  groups               = each.value.groups != null ? each.value.groups : null
  home_phone_number    = each.value.home_phone_number
  mobile_phone_number  = each.value.mobile_phone_number
  enabled_capabilities = each.value.enabled_capabilities

  #Optional
  defined_tags        = each.value.defined_tags
  freeform_tags_key   = each.value.freeform_tags != null ? each.value.freeform_tags.key : null
  freeform_tags_value = each.value.freeform_tags != null ? each.value.freeform_tags.value : null
}