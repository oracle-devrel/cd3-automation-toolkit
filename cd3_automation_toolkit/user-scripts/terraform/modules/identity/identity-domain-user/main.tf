// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
  idcs_endpoint  = data.oci_identity_domains.iam_domains.domains[0].url
  user_name      = var.user_name
  emails {
    primary    = "true"
    secondary  = "false"
    type       = "work"
    value      =  var.email
    verified   = "false"
  }

  urnietfparamsscimschemasoracleidcsextensioncapabilities_user  {
    can_use_api_keys                 = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_api_keys
    can_use_auth_tokens              = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_auth_tokens
    can_use_console_password         = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_console_password
    can_use_customer_secret_keys     = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_customer_secret_keys
    can_use_db_credentials           = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_db_credentials
    can_use_oauth2client_credentials = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_oauth2client_credentials
    can_use_smtp_credentials         = var.urnietfparamsscimschemasoracleidcsextensioncapabilities_user.can_use_smtp_credentials
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




