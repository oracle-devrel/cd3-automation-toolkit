############################
# Module Block - Identity
# Create Groups
############################

module "iam-groups" {

  source            = "./modules/identity/iam-group"
  for_each          = var.groups
  depends_on        = [module.iam-users]
  tenancy_ocid      = var.tenancy_ocid
  group_name        = each.value.group_name
  group_description = each.value.group_description
  matching_rule     = each.value.matching_rule
  members           = lookup(each.value, "members", [])

  #Optional
  defined_tags  = each.value.defined_tags
  freeform_tags = each.value.freeform_tags
}

module "groups" {

  depends_on = [module.users]

  source   = "./modules/identity/identity-domain-group"
  for_each = var.identity_domain_groups

  group_name        = each.value.group_name
  group_description = each.value.group_description != null ? each.value.group_description : null
  matching_rule     = each.value.matching_rule
  compartment_id    = each.value.domain_compartment_id != "root" ? (length(regexall("ocid1.compartment.oc*", each.value.domain_compartment_id)) > 0 ? each.value.domain_compartment_id : var.compartment_ocids[each.value.domain_compartment_id]) : var.tenancy_ocid
  identity_domain   = data.oci_identity_domains.iam_domains[each.value.idcs_endpoint].domains[0]
  tenancy_ocid      = var.tenancy_ocid
  members           = each.value.members != null ? each.value.members : []
  domain_users      = local.domain_users_map[each.value.idcs_endpoint]
  #Optional
  user_can_request_access = each.value.user_can_request_access
  defined_tags            = each.value.defined_tags
  freeform_tags_key       = each.value.freeform_tags != null ? each.value.freeform_tags.key : null
  freeform_tags_value     = each.value.freeform_tags != null ? each.value.freeform_tags.value : null

}