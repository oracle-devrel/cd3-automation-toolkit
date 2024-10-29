# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Identity
# Create Compartments
############################

module "iam-compartments" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.root != null ? var.compartments.root : {}

  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = each.value.parent_compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])) : var.tenancy_ocid
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level1" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level1 != null ? var.compartments.compartment_level1 : {}

  depends_on = [module.iam-compartments]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(merge(module.iam-compartments.*...)[each.value.parent_compartment_id]["compartment_tf_id"], var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level2" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level2 != null ? var.compartments.compartment_level2 : {}

  depends_on = [module.sub-compartments-level1]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(merge(module.sub-compartments-level1.*...)[each.value.parent_compartment_id]["compartment_tf_id"], var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])
  compartment_name        = each.value.name
  compartment_description = each.value.description

  enable_delete = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level3" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level3 != null ? var.compartments.compartment_level3 : {}

  depends_on = [module.sub-compartments-level2]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(merge(module.sub-compartments-level2.*...)[each.value.parent_compartment_id]["compartment_tf_id"], var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level4" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level4 != null ? var.compartments.compartment_level4 : {}

  depends_on = [module.sub-compartments-level3]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(merge(module.sub-compartments-level3.*...)[each.value.parent_compartment_id]["compartment_tf_id"], var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "sub-compartments-level5" {
  source   = "./modules/identity/iam-compartment"
  for_each = var.compartments.compartment_level5 != null ? var.compartments.compartment_level5 : {}

  depends_on = [module.sub-compartments-level4]
  # insert the 4 required variables here
  tenancy_ocid            = var.tenancy_ocid
  compartment_id          = length(regexall("ocid1.compartment.oc*", each.value.parent_compartment_id)) > 0 ? each.value.parent_compartment_id : try(merge(module.sub-compartments-level4.*...)[each.value.parent_compartment_id]["compartment_tf_id"], var.compartment_ocids[each.value.parent_compartment_id], zipmap(data.oci_identity_compartments.compartments.compartments.*.name, data.oci_identity_compartments.compartments.compartments.*.id)[each.value.parent_compartment_id])
  compartment_name        = each.value.name
  compartment_description = each.value.description
  enable_delete           = each.value.enable_delete

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

/*
output "root_compartments_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.iam-compartments.*...) : v.compartment_tf_id]
}

output "sub_compartments_level1_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level1.*...) : v.compartment_tf_id]
}

output "sub_compartments_level2_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level2.*...) : v.compartment_tf_id]
}

output "sub_compartments_level3_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level3.*...) : v.compartment_tf_id]
}

output "sub_compartments_level4_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level4.*...) : v.compartment_tf_id]
}

output "sub_compartments_level5_map" {
  description = "Compartment ocid"
  // This allows the compartment ID to be retrieved from the resource if it exists, and if not to use the data source.
  #value = element(concat(oci_identity_compartment.this.*.id, tolist([""])), 0)
  value = [ for k,v in merge(module.sub-compartments-level5.*...) : v.compartment_tf_id]
}
*/


############################
# Module Block - Identity
# Create Groups
############################

module "iam-groups" {

  source   = "./modules/identity/iam-group"
  for_each = var.groups
  depends_on       = [module.iam-users]
  tenancy_ocid      = var.tenancy_ocid
  group_name        = each.value.group_name
  group_description = each.value.group_description
  matching_rule     = each.value.matching_rule
  members           = lookup(each.value, "members", [])

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
# Create Policies
############################

module "iam-policies" {
  source   = "./modules/identity/iam-policy"
  for_each = var.policies

  depends_on            = [module.iam-groups]
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

/*
output "policies_id_map" {
  value = [ for k,v in merge(module.iam-policies.*...) : v.policies_id_map]
}
*/

############################
# Module Block - Identity
# Create Users
############################

module "iam-users" {
  source           = "./modules/identity/iam-user"
  #depends_on       = [module.iam-groups]
  for_each         = var.users
  user_name        = each.value.name
  user_description = each.value.description
  user_email       = each.value.email
  tenancy_ocid         = var.tenancy_ocid
  enabled_capabilities = each.value.enabled_capabilities != null ? each.value.enabled_capabilities : null

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}



############################
# Module - Network Source
# Create Network Source
############################

#locals {
#
#vcns = flatten ([
#for key, val in var.networkSources : [
# for k,virtual_source in val.virtual_source_list  != null ? val.virtual_source_list : [] :{
#	 vcn_name = virtual_source.vcn_name.0
#	 network_compartment = virtual_source.network_compartment_id.0
#	 }
#	]
#])
#}

#data "oci_core_vcns" "oci_vcns_networksource" {
#
#	for_each        = { for vcn in local.vcns : vcn.vcn_name => vcn... }
#	display_name    = each.key
#	compartment_id  = var.compartment_ocids[each.value[0].network_compartment]
#}

module "iam-network-sources" {
  source       = "./modules/identity/iam-network-sources"
  for_each     = var.networkSources
  name         = each.value.name
  description  = each.value.description
  tenancy_ocid = var.tenancy_ocid

  #Optional
  public_source_list = each.value.public_source_list != null ? each.value.public_source_list : null
  #virtual_source_list  = each.value.virtual_source_list != null ? each.value.virtual_source_list : null
  virtual_source_list = { for k, v in each.value.virtual_source_list != null ? each.value.virtual_source_list : [] : k =>
    {
      #vcn_id = data.oci_core_vcns.oci_vcns_networksource[v.vcn_name.0].virtual_networks.*.id[0]
      ip_ranges = v.ip_ranges
  } }
  #vcn_comp_map = each.value.vcn_comp_map != null ? each.value.vcn_comp_map : null
  defined_tags  = try(each.value.defined_tags, null)
  freeform_tags = try(each.value.freeform_tags, null)
}
############################
# Module Block - Identity
# Create Identity Domain Groups
############################
data "oci_identity_domains" "iam_domains" {
  for_each = merge(var.identity_domain_groups,var.identity_domain_users)
  # Required
  compartment_id = var.compartment_ocids[each.value.domain_compartment_id]
  # Optional
  display_name = each.value.idcs_endpoint
}

module "groups" {

  depends_on = [module.users]

  source   = "./modules/identity/identity-domain-group"
  for_each = var.identity_domain_groups

  group_name               = each.value.group_name
  group_description        = each.value.group_description != null ? each.value.group_description : null
  matching_rule            = each.value.matching_rule
  compartment_id           = each.value.domain_compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.domain_compartment_id)) > 0 ? each.value.domain_compartment_id : var.compartment_ocids[each.value.domain_compartment_id]) : var.tenancy_ocid
  identity_domain          = data.oci_identity_domains.iam_domains[each.key].domains[0]
  tenancy_ocid             = var.tenancy_ocid
  members                  = each.value.members != null ? each.value.members : []

  #Optional
  user_can_request_access  = each.value.user_can_request_access
  defined_tags             = each.value.defined_tags
  freeform_tags_key        = each.value.freeform_tags != null ? each.value.freeform_tags.key : null
  freeform_tags_value      = each.value.freeform_tags != null ? each.value.freeform_tags.value : null

}

############################
# Module Block - Identity
# Create Identity Domain Users
############################

module "users" {
  source           = "./modules/identity/identity-domain-user"
  #depends_on       = [module.iam-groups]
  for_each         = var.identity_domain_users
  user_name        = each.value.user_name
  family_name      = each.value.name.family_name
  given_name       = each.value.name.given_name
  middle_name      = each.value.name.middle_name
  honorific_prefix = each.value.name.honorific_prefix
  display_name     = each.value.display_name
  identity_domain  = data.oci_identity_domains.iam_domains[each.key].domains[0]
  compartment_id   = each.value.domain_compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.domain_compartment_id)) > 0 ? each.value.domain_compartment_id : var.compartment_ocids[each.value.domain_compartment_id]) : var.tenancy_ocid
  description      = each.value.description
  email            = each.value.email
  recovery_email   = each.value.recovery_email
  tenancy_ocid     = var.tenancy_ocid
  groups           = each.value.groups != null ? each.value.groups : null
  home_phone_number = each.value.home_phone_number
  mobile_phone_number = each.value.mobile_phone_number
  enabled_capabilities = each.value.enabled_capabilities

  #Optional
  defined_tags             = each.value.defined_tags
  freeform_tags_key        = each.value.freeform_tags != null ? each.value.freeform_tags.key : null
  freeform_tags_value      = each.value.freeform_tags != null ? each.value.freeform_tags.value : null
}