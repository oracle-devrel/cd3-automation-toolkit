// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Resource Block - Identity
# Create Users
############################

resource "oci_identity_user" "user" {

  #Required
  compartment_id = var.tenancy_ocid
  description    = var.user_description
  name           = var.user_name
  email          = var.user_email

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

}

resource "oci_identity_user_group_membership" "user_group_membership" {
  count      = var.group_membership != null ? length(var.group_membership) : 0
  depends_on = [oci_identity_user.user]
  user_id    = oci_identity_user.user.id
  group_id   = length(regexall("ocid1.group.oc*", var.group_membership[count.index])) > 0 ? var.group_membership[count.index] : data.oci_identity_groups.iam_groups.groups[index(data.oci_identity_groups.iam_groups.groups.*.name, var.group_membership[count.index])].id
}

resource "oci_identity_user_capabilities_management" "user_capabilities_management" {
  count      = var.disable_capabilities != null ? 1 : 0
  depends_on = [oci_identity_user.user]
  user_id    = oci_identity_user.user.id

  can_use_api_keys             = var.disable_capabilities != null && contains(var.disable_capabilities, "can_use_api_keys") ? false : true
  can_use_auth_tokens          = var.disable_capabilities != null && contains(var.disable_capabilities, "can_use_auth_tokens") ? false : true
  can_use_console_password     = var.disable_capabilities != null && contains(var.disable_capabilities, "can_use_console_password") ? false : true
  can_use_customer_secret_keys = var.disable_capabilities != null && contains(var.disable_capabilities, "can_use_customer_secret_keys") ? false : true
  can_use_smtp_credentials     = var.disable_capabilities != null && contains(var.disable_capabilities, "can_use_smtp_credentials") ? false : true

}
