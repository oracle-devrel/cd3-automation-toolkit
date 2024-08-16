# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Resource Block - Identity
# Create Users
############################

resource "oci_identity_domains_user" "user" {

  #Required
  schemas = ["urn:ietf:params:scim:schemas:core:2.0:User",
             "urn:ietf:params:scim:schemas:oracle:idcs:extension:userState:User",
             "urn:ietf:params:scim:schemas:oracle:idcs:extension:OCITags",
             "urn:ietf:params:scim:schemas:oracle:idcs:extension:capabilities:User",
             "urn:ietf:params:scim:schemas:oracle:idcs:extension:user:User"]
  description   = var.description
  name {
    family_name = var.family_name
  }
  idcs_endpoint = var.identity_domain.url
  user_name      = var.user_name
  emails {
    primary    = "true"
    secondary  = "false"
    type       = "work"
    value      =  var.email
    verified   = "false"
  }

  urnietfparamsscimschemasoracleidcsextensioncapabilities_user  {

    can_use_api_keys             = contains(var.enabled_capabilities, "api_keys") ? true :false
    can_use_auth_tokens          = contains(var.enabled_capabilities, "auth_tokens") ? true :false
    can_use_console_password     = contains(var.enabled_capabilities, "console_password") ? true :false
    can_use_customer_secret_keys = contains(var.enabled_capabilities, "customer_secret_keys") ? true :false
    can_use_smtp_credentials     = contains(var.enabled_capabilities, "smtp_credentials") ? true :false
    can_use_db_credentials       = contains(var.enabled_capabilities, "db_credentials") ? true :false
    can_use_oauth2client_credentials = contains(var.enabled_capabilities, "oauth2client_credentials") ? true :false
  }
 dynamic "urnietfparamsscimschemasoracleidcsextension_oci_tags" {
  for_each = var.defined_tags != null ? [1] :[]
  content{
    # Optional
    dynamic "defined_tags" {
      for_each = var.defined_tags
      content {
        key       = defined_tags.value.key
        namespace = defined_tags.value.namespace
        value     = defined_tags.value.value
      }
    }
    dynamic "freeform_tags" {
      for_each = var.freeform_tags_key != null && var.freeform_tags_value != null ? [1] : []
      content {
        key   = var.freeform_tags_key
        value = var.freeform_tags_value
      }
    }
    }
  }
  lifecycle {
    ignore_changes = [
      schemas,
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedOn"],
      urnietfparamsscimschemasoracleidcsextension_oci_tags["defined_tags.CreatedBy"],
      emails
    ]
  }
}




