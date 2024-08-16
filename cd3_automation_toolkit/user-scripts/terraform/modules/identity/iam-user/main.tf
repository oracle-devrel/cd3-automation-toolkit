# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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

resource "oci_identity_user_capabilities_management" "user_capabilities_management" {
  count      = var.enabled_capabilities != null ? 1 : 0
  depends_on = [oci_identity_user.user]
  user_id    = oci_identity_user.user.id

  can_use_api_keys             = contains(var.enabled_capabilities, "api_keys") ? true :false
  can_use_auth_tokens          = contains(var.enabled_capabilities, "auth_tokens") ? true :false
  can_use_console_password     = contains(var.enabled_capabilities, "console_password") ? true :false
  can_use_customer_secret_keys = contains(var.enabled_capabilities, "customer_secret_keys") ? true :false
  can_use_smtp_credentials     = contains(var.enabled_capabilities, "smtp_credentials") ? true :false
}
