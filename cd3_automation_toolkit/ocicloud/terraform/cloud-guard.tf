# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Module Block - Security
# Create Cloud Guard Configuration and Cloud Guard Targets
############################

module "cloud-guard-configurations" {
  source   = "./modules/security/cloud-guard-configuration"
  for_each = var.cloud_guard_configs != null ? var.cloud_guard_configs : {}

  #Required
  compartment_id   = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  reporting_region = each.value.reporting_region
  status           = each.value.status

  #Optional
  self_manage_resources = each.value.self_manage_resources
}

module "cloud-guard-targets" {
  source   = "./modules/security/cloud-guard-target"
  for_each = var.cloud_guard_targets != null ? var.cloud_guard_targets : {}

  depends_on = [module.cloud-guard-configurations]
  #Required
  tenancy_ocid         = var.tenancy_ocid
  compartment_id       = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : var.tenancy_ocid
  display_name         = each.value.display_name
  target_resource_id   = each.value.target_resource_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.target_resource_id)) > 0 ? each.value.target_resource_id : var.compartment_ocids[each.value.target_resource_id]) : each.value.target_resource_id
  target_resource_type = each.value.target_resource_type != null ? each.value.target_resource_type : "COMPARTMENT"
  prefix               = each.value.prefix

  #Optional
  defined_tags                    = each.value.defined_tags
  description                     = each.value.description
  freeform_tags                   = each.value.freeform_tags
  state                           = each.value.state
  target_detector_recipes         = each.value.target_detector_recipes
  target_responder_recipes        = each.value.target_responder_recipes
  detector_recipe_rule_overrides  = each.value.rule_mode == "custom_rules" ? local.detector_recipe_rule_catalog : {}
  responder_recipe_rule_overrides = each.value.rule_mode == "custom_rules" ? local.responder_recipe_rule_catalog : {}
}

# Cloud Guard Rule Catalogue.
#
# Keep tenancy, compartment, target, and recipe-prefix settings in
# cis-cloudguard.auto.tfvars. Below section contains recipe-rule settings.
# Modify each rule as per requirement.
# For each Cloud Guard target, set rule_mode to one of:
#   default_rules  - clone Oracle-managed recipes without Terraform rule overrides.
#   custom_rules  - apply every rule in this catalogue.
#
# To customize the baseline, edit is_enabled, risk_level, or labels below.

locals {
  detector_recipe_rule_catalog = {
    "OCI Activity Detector Recipe" = {
      BASTION_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Bastion created"
        detector_rule_id = "BASTION_CREATED"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["Bastion"]
      },
      BASTION_SESSION_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Bastion session created"
        detector_rule_id = "BASTION_SESSION_CREATED"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["Bastion"]
      },
      CA_BUNDLE_UPDATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "CA bundle updated"
        detector_rule_id = "CA_BUNDLE_UPDATED"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["Certificates"]
      },
      CERTIFICATE_AUTHORITY_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Certificate Authority (CA) deleted"
        detector_rule_id = "CERTIFICATE_AUTHORITY_DELETED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Certificates"]
      },
      DRG_ATTACHED_TO_VCN = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "DRG attached to a VCN"
        detector_rule_id = "DRG_ATTACHED_TO_VCN"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      DRG_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "DRG created"
        detector_rule_id = "DRG_CREATED"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      DRG_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "DRG deleted"
        detector_rule_id = "DRG_DELETED"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      DRG_DETACHED_FROM_VCN = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "DRG detached from a VCN"
        detector_rule_id = "DRG_DETACHED_FROM_VCN"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      DATABASE_SYSTEM_TERMINATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Database System terminated"
        detector_rule_id = "DATABASE_SYSTEM_TERMINATED"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Database"]
      },
      EXPORT_IMAGE = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Export Image"
        detector_rule_id = "EXPORT_IMAGE"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["Compute"]
      },
      IAM_API_KEY_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM API keys created"
        detector_rule_id = "IAM_API_KEY_CREATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_API_KEY_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM API keys deleted"
        detector_rule_id = "IAM_API_KEY_DELETED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_AUTH_TOKEN_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Auth token created"
        detector_rule_id = "IAM_AUTH_TOKEN_CREATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_AUTH_TOKEN_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Auth token deleted"
        detector_rule_id = "IAM_AUTH_TOKEN_DELETED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_CUSTOMER_KEY_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Customer keys created"
        detector_rule_id = "IAM_CUSTOMER_KEY_CREATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_CUSTOMER_KEY_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Customer keys deleted"
        detector_rule_id = "IAM_CUSTOMER_KEY_DELETED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_GROUP_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Group created"
        detector_rule_id = "IAM_GROUP_CREATED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM", "CIS_OCI_V_2.0.0"]
      },
      IAM_GROUP_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM Group deleted"
        detector_rule_id = "IAM_GROUP_DELETED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM", "CIS_OCI_V_2.0.0"]
      },
      IAM_OAUTH_CREDENTIAL_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM OAuth 2.0 credentials created"
        detector_rule_id = "IAM_OAUTH_CREDENTIAL_CREATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_OAUTH_CREDENTIAL_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM OAuth 2.0 credentials deleted"
        detector_rule_id = "IAM_OAUTH_CREDENTIAL_DELETED"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      NON_IAM_USER_SMTP_CREDENTIAL = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM USER SMTP Credential Rotation"
        detector_rule_id = "NON_IAM_USER_SMTP_CREDENTIAL"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },
      IAM_USER_UI_PASSWORD_CREATED_OR_RESET = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM User UI password created or reset"
        detector_rule_id = "IAM_USER_UI_PASSWORD_CREATED_OR_RESET"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["IAM_Credentials", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_USER_CAPABILITIES_MODIFIED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM User capabilities modified"
        detector_rule_id = "IAM_USER_CAPABILITIES_MODIFIED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IAM_USER_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "IAM User created"
        detector_rule_id = "IAM_USER_CREATED"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      IMPORT_IMAGE = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Import Image"
        detector_rule_id = "IMPORT_IMAGE"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["Compute"]
      },
      INSTANCE_TERMINATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Instance terminated"
        detector_rule_id = "INSTANCE_TERMINATED"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Compute"]
      },
      INTERMEDIATE_CERTIFICATE_AUTHORITY_REVOKED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Intermediate Certificate Authority (CA) revoked"
        detector_rule_id = "INTERMEDIATE_CERTIFICATE_AUTHORITY_REVOKED"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Certificates"]
      },
      NON_MFA_USER_LOGIN = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Local user authenticated without MFA"
        detector_rule_id = "NON_MFA_USER_LOGIN"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM"]
      },
      SECURITY_POLICY_MODIFIED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Security policy modified"
        detector_rule_id = "SECURITY_POLICY_MODIFIED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.1_MONITORING", "IAM", "CIS_OCI_V_2.0.0"]
      },
      SUBNET_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Subnet Changed"
        detector_rule_id = "SUBNET_CHANGED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["Network"]
      },
      SUBNET_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Subnet deleted"
        detector_rule_id = "SUBNET_DELETED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["Network"]
      },
      SUSPICIOUS_IP_ACTIVITY = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Suspicious Ip Activity"
        detector_rule_id = "SUSPICIOUS_IP_ACTIVITY"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Network"]
      },
      UPDATE_IMAGE = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "Update Image"
        detector_rule_id = "UPDATE_IMAGE"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["Compute"]
      },
      USER_ADDED_TO_GROUP = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "User added to group"
        detector_rule_id = "USER_ADDED_TO_GROUP"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "IAM", "CIS_OCI_V_2.0.0"]
      },
      USER_REMOVED_FROM_GROUP = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "User removed from group"
        detector_rule_id = "USER_REMOVED_FROM_GROUP"
        is_enabled       = false
        risk_level       = "MINOR"
        labels           = ["IAM", "CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "CIS_OCI_V_2.0.0"]
      },
      VCN_DHCP_OPTION_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN DHCP Option changed"
        detector_rule_id = "VCN_DHCP_OPTION_CHANGED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network"]
      },
      INTERNET_GATEWAY_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Internet Gateway created"
        detector_rule_id = "INTERNET_GATEWAY_CREATED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      INTERNET_GATEWAY_TERMINATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Internet Gateway terminated"
        detector_rule_id = "INTERNET_GATEWAY_TERMINATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_LOCAL_PEERING_GATEWAY_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Local Peering Gateway changed"
        detector_rule_id = "VCN_LOCAL_PEERING_GATEWAY_CHANGED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      NSG_DELETE = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Network Security Group Deleted"
        detector_rule_id = "NSG_DELETE"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      NSG_EGRESS_RULE_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Network Security Group egress rule changed"
        detector_rule_id = "NSG_EGRESS_RULE_CHANGED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      NSG_INGRESS_RULE_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Network Security Group ingress rule changed"
        detector_rule_id = "NSG_INGRESS_RULE_CHANGED"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_SECURITY_LIST_CREATED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Security List created"
        detector_rule_id = "VCN_SECURITY_LIST_CREATED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_SECURITY_LIST_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Security List deleted"
        detector_rule_id = "VCN_SECURITY_LIST_DELETED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_SECURITY_LIST_EGRESS_RULES_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Security List egress rules changed"
        detector_rule_id = "VCN_SECURITY_LIST_EGRESS_RULES_CHANGED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_SECURITY_LIST_INGRESS_RULES_CHANGED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN Security List ingress rules changed"
        detector_rule_id = "VCN_SECURITY_LIST_INGRESS_RULES_CHANGED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_CREATE = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN created"
        detector_rule_id = "VCN_CREATE"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      },
      VCN_DELETED = {
        #display_name_CUSTOM_OCI_Activity_Detector_Recipe = "VCN deleted"
        detector_rule_id = "VCN_DELETED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "Network", "CIS_OCI_V_2.0.0"]
      }
    }

    "OCI Configuration Detector Recipe" = {
      #display_name_custom_configuration_detector_recipe = "API key is too old"
      API_KEY_TOO_OLD = {
        detector_rule_id = "API_KEY_TOO_OLD"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Admin group has too many members"
      ADMIN_GROUP_HAS_TOO_MANY_MEMBERS = {
        detector_rule_id = "ADMIN_GROUP_HAS_TOO_MANY_MEMBERS"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "BOAT group is given privileges by policies"
      JIT_DISABLED_BOAT_GROUP_HAS_PRIVILEGES = {
        detector_rule_id = "JIT_DISABLED_BOAT_GROUP_HAS_PRIVILEGES"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Block Volume is encrypted with Oracle-managed key"
      BLOCK_VOLUME_ENCRYPTED_WITH_ORACLE_MANAGED_KEY = {
        detector_rule_id = "BLOCK_VOLUME_ENCRYPTED_WITH_ORACLE_MANAGED_KEY"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["Storage", "KMS", "CIS_OCI_V_2.0.0"]
      },

      #display_name_custom_configuration_detector_recipe = "Block Volume is not attached"
      BLOCK_VOLUME_NOT_ATTACHED = {
        detector_rule_id = "BLOCK_VOLUME_NOT_ATTACHED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Storage"]
      },

      #display_name_custom_configuration_detector_recipe = "Bucket is public"
      BUCKET_IS_PUBLIC = {
        detector_rule_id = "BUCKET_IS_PUBLIC"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["CIS_OCI_V1.1_OBJECTSTORAGE", "ObjectStorage", "CIS_OCI_V_2.0.0"]
      },

      #display_name_custom_configuration_detector_recipe = "Data Safe is not enabled"
      DATA_SAFE_NOT_ENABLED = {
        detector_rule_id = "DATA_SAFE_NOT_ENABLED"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Database Security"]
      },

      #display_name_custom_configuration_detector_recipe = "Database System has public IP address"
      DATABASE_HAS_PUBLIC_IP = {
        detector_rule_id = "DATABASE_HAS_PUBLIC_IP"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database System is publicly accessible"
      DATABASE_PUBLICLY_ACCESSIBLE = {
        detector_rule_id = "DATABASE_PUBLICLY_ACCESSIBLE"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database System version is not sanctioned"
      DATABASE_SYSTEM_VERSION_NOT_SANCTIONED = {
        detector_rule_id = "DATABASE_SYSTEM_VERSION_NOT_SANCTIONED"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database is not backed up automatically"
      DATABASE_HAS_NO_AUTO_BACKUP = {
        detector_rule_id = "DATABASE_HAS_NO_AUTO_BACKUP"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database is not registered in Data Safe"
      DATA_SAFE_DB_NOT_REGISTERED = {
        detector_rule_id = "DATA_SAFE_DB_NOT_REGISTERED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Database Security"]
      },

      #display_name_custom_configuration_detector_recipe = "Database patch is not applied"
      DATABASE_PATCH_NOT_APPLIED = {
        detector_rule_id = "DATABASE_PATCH_NOT_APPLIED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database system patch is not applied"
      DATABASE_SYSTEM_PATCH_NOT_APPLIED = {
        detector_rule_id = "DATABASE_SYSTEM_PATCH_NOT_APPLIED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "Database version is not sanctioned"
      DATABASE_VERSION_NOT_SANCTIONED = {
        detector_rule_id = "DATABASE_VERSION_NOT_SANCTIONED"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Database"]
      },

      #display_name_custom_configuration_detector_recipe = "IAM Auth token is too old"
      AUTH_TOKEN_TOO_OLD = {
        detector_rule_id = "AUTH_TOKEN_TOO_OLD"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "IAM Customer secret key is too old"
      SECRET_KEY_TOO_OLD = {
        detector_rule_id = "SECRET_KEY_TOO_OLD"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "IAM MFA TOTP Device is too old"
      IAM_MFA_TOTP_DEVICE_TOO_OLD = {
        detector_rule_id = "IAM_MFA_TOTP_DEVICE_TOO_OLD"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "IAM group has too few members"
      OCI_IAM_GRP_FEW_MEMBERS_FOUND = {
        detector_rule_id = "OCI_IAM_GRP_FEW_MEMBERS_FOUND"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Instance has a public IP address"
      INSTANCE_WITH_PUBLIC_IP = {
        detector_rule_id = "INSTANCE_WITH_PUBLIC_IP"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_NETWORK", "CIS_OCI_V1.1_NETWORK", "Compute"]
      },

      #display_name_custom_configuration_detector_recipe = "Instance is not running an Oracle public image"
      INSTANCE_NOT_RUNNING_OPC = {
        detector_rule_id = "INSTANCE_NOT_RUNNING_OPC"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["Compute"]
      },

      #display_name_custom_configuration_detector_recipe = "Instance is publicly accessible"
      INSTANCE_PUBLICLY_ACCESSIBLE = {
        detector_rule_id = "INSTANCE_PUBLICLY_ACCESSIBLE"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Compute"]
      },

      #display_name_custom_configuration_detector_recipe = "Instance is running an Oracle public image"
      INSTANCE_RUNNING_OPC = {
        detector_rule_id = "INSTANCE_RUNNING_OPC"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["Compute"]
      },

      #display_name_custom_configuration_detector_recipe = "Instance is running without required Tags"
      INSTANCE_WITHOUT_REQUIRED_TAGS = {
        detector_rule_id = "INSTANCE_WITHOUT_REQUIRED_TAGS"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "TAGS"]
      },

      #display_name_custom_configuration_detector_recipe = "Key has not been rotated"
      KEY_NOT_ROTATED = {
        detector_rule_id = "KEY_NOT_ROTATED"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.1_MONITORING", "KMS"]
      },

      #display_name_custom_configuration_detector_recipe = "Load Balancer has public IP address"
      LB_HAS_PUBLIC_IP = {
        detector_rule_id = "LB_HAS_PUBLIC_IP"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Load balancer SSL certificate expiring soon"
      LB_CERTIFICATE_EXPIRING_SOON = {
        detector_rule_id = "LB_CERTIFICATE_EXPIRING_SOON"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Load balancer allows weak SSL communication"
      LB_WEAK_SSL_COMMUNICATION = {
        detector_rule_id = "LB_WEAK_SSL_COMMUNICATION"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Load balancer allows weak cipher suite"
      LB_WEAK_CIPHER_SUITE = {
        detector_rule_id = "LB_WEAK_CIPHER_SUITE"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Load balancer has no back-end set"
      LB_NO_BACK_END_SET = {
        detector_rule_id = "LB_NO_BACK_END_SET"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Load balancer has no inbound rules or listeners"
      LB_NO_INBOUND_RULES_OR_LISTENERS = {
        detector_rule_id = "LB_NO_INBOUND_RULES_OR_LISTENERS"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "NSG egress rule contains disallowed IP/port"
      VCN_NSG_EGRESS_RULE_PORTS_CHECK = {
        detector_rule_id = "VCN_NSG_EGRESS_RULE_PORTS_CHECK"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_NETWORK", "CIS_OCI_V1.1_NETWORK", "Network"]
      },

      #display_name_custom_configuration_detector_recipe = "NSG ingress rule contains disallowed IP/port"
      VCN_NSG_INGRESS_RULE_PORTS_CHECK = {
        detector_rule_id = "VCN_NSG_INGRESS_RULE_PORTS_CHECK"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_NETWORK", "CIS_OCI_V1.1_NETWORK", "Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Object Storage bucket is encrypted with Oracle-managed key"
      BUCKET_ENCRYPTED_WITH_ORACLE_MANAGED_KEY = {
        detector_rule_id = "BUCKET_ENCRYPTED_WITH_ORACLE_MANAGED_KEY"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["CIS_OCI_V1.1_ObjectStorage", "ObjectStorage", "KMS"]
      },

      #display_name_custom_configuration_detector_recipe = "Password is too old"
      PASSWORD_TOO_OLD = {
        detector_rule_id = "PASSWORD_TOO_OLD"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Password policy does not meet complexity requirements"
      PASSWORD_POLICY_NOT_COMPLEX = {
        detector_rule_id = "PASSWORD_POLICY_NOT_COMPLEX"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Policy gives too many privileges"
      POLICY_GIVES_MANY_PRIVILEGES = {
        detector_rule_id = "POLICY_GIVES_MANY_PRIVILEGES"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Policy uses "any-user""
      POLICY_USES_ANY_USER = {
        detector_rule_id = "POLICY_USES_ANY_USER"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "Read Log access disabled for bucket"
      BUCKET_READ_LOG_ACCESS_DISABLED = {
        detector_rule_id = "BUCKET_READ_LOG_ACCESS_DISABLED"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.1_ObjectStorage", "ObjectStorage"]
      },

      #display_name_custom_configuration_detector_recipe = "Resource is not tagged appropriately"
      RESOURCE_NOT_TAGGED = {
        detector_rule_id = "RESOURCE_NOT_TAGGED"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_MONITORING", "CIS_OCI_V1.1_MONITORING", "TAGS"]
      },

      #display_name_custom_configuration_detector_recipe = "Scanned container image has vulnerabilities"
      SCANNED_CONTAINER_IMAGE_VULNERABILITY = {
        detector_rule_id = "SCANNED_CONTAINER_IMAGE_VULNERABILITY"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["VSS"]
      },

      #display_name_custom_configuration_detector_recipe = "Scanned host has open ports"
      SCANNED_HOST_OPEN_PORTS = {
        detector_rule_id = "SCANNED_HOST_OPEN_PORTS"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["VSS"]
      },

      #display_name_custom_configuration_detector_recipe = "Scanned host has vulnerabilities"
      SCANNED_HOST_VULNERABILITY = {
        detector_rule_id = "SCANNED_HOST_VULNERABILITY"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["VSS"]
      },

      #display_name_custom_configuration_detector_recipe = "Tenancy admin privilege granted to group"
      POLICY_TENANCY_ADMIN_GROUP_PRIVILEGES = {
        detector_rule_id = "POLICY_TENANCY_ADMIN_GROUP_PRIVILEGES"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User does not have MFA enabled"
      NO_MFA_ENABLED_FOR_USER = {
        detector_rule_id = "NO_MFA_ENABLED_FOR_USER"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User exists within tenancy with nonstandard naming convention"
      USER_EXISTS_WITHIN_TENANCY_WITH_NON_STANDARD_NAMING_CONVENTION = {
        detector_rule_id = "USER_EXISTS_WITHIN_TENANCY_WITH_NON_STANDARD_NAMING_CONVENTION"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["CIS_OCI_V1.1_IAM", "CIS_OCI_V1.0_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has API keys"
      USER_HAS_API_KEYS = {
        detector_rule_id = "USER_HAS_API_KEYS"
        is_enabled       = true
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has Api Key Capability"
      USER_HAS_API_KEY_CAPABILITY = {
        detector_rule_id = "USER_HAS_API_KEY_CAPABILITY"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has Auth Token Capability"
      USER_HAS_AUTH_TOKEN_CAPABILITY = {
        detector_rule_id = "USER_HAS_AUTH_TOKEN_CAPABILITY"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has Console Password Capability"
      USER_HAS_CONSOLE_PASSWORD_CAPABILITY = {
        detector_rule_id = "USER_HAS_CONSOLE_PASSWORD_CAPABILITY"
        is_enabled       = true
        risk_level       = "CRITICAL"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has Customer Secret Key Capability"
      USER_HAS_CUSTOMER_SECRET_CAPABILITY = {
        detector_rule_id = "USER_HAS_CUSTOMER_SECRET_CAPABILITY"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has DB Credential Capability"
      USER_HAS_DB_CREDENTIAL_CAPABILITY = {
        detector_rule_id = "USER_HAS_DB_CREDENTIAL_CAPABILITY"
        is_enabled       = true
        risk_level       = "HIGH"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has OAuth2 Credential Capability"
      USER_HAS_OAUTH_CREDENTIAL_CAPABILITY = {
        detector_rule_id = "USER_HAS_OAUTH_CREDENTIAL_CAPABILITY"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "User has SMTP Credential Capability"
      USER_HAS_SMTP_CREDENTIAL_CAPABILITY = {
        detector_rule_id = "USER_HAS_SMTP_CREDENTIAL_CAPABILITY"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "VCN has no inbound Security List"
      VCN_NO_INBOUND_SECURITY_LIST = {
        detector_rule_id = "VCN_NO_INBOUND_SECURITY_LIST"
        is_enabled       = true
        risk_level       = "MEDIUM"
        labels           = ["CIS_OCI_V1.0_IAM", "CIS_OCI_V1.1_IAM", "IAM"]
      },

      #display_name_custom_configuration_detector_recipe = "VNIC without associated network security group"
      VNIC_WITHOUT_NETWORK_SECURITY_GROUP = {
        detector_rule_id = "VNIC_WITHOUT_NETWORK_SECURITY_GROUP"
        is_enabled       = true
        risk_level       = "MINOR"
        labels           = ["Network"]
      },

      #display_name_custom_configuration_detector_recipe = "Write Log access disabled for bucket"
      BUCKET_WRITE_LOG_ACCESS_DISABLED = {
        detector_rule_id = "BUCKET_WRITE_LOG_ACCESS_DISABLED"
        is_enabled       = false
        risk_level       = "LOW"
        labels           = ["CIS_OCI_V1.1_MONITORING", "CIS_OCI_V1.1_ObjectStorage", "ObjectStorage"]
      }

    }

    "OCI Instance Security Detector Recipe" = {
    }

    "OCI Threat Detector Recipe" = {
      "Rogue_user" = {
        #display_name_custom_threat_detector_recipe = "Rogue User"
        detector_rule_id = "ROGUE_USER"
        is_enabled       = true # This value should be set to true always as it is a default rule and not recommended to modify it.
        risk_level       = "CRITICAL"
        labels           = []
      }
    }
  }

  responder_recipe_rule_catalog = {
    "OCI Responder Recipe" = {
      "delete_internet_gateway" = {
        responder_rule_id = "DELETE_INTERNET_GATEWAY"
        is_enabled        = true
      }

      "cloud_event" = {
        responder_rule_id = "EVENT"
        is_enabled        = true
      }

      "make_bucket_private" = {
        responder_rule_id = "MAKE_BUCKET_PRIVATE"
        is_enabled        = true
      }

      "delete_public_ip" = {
        responder_rule_id = "DELETE_PUBLIC_IP"
        is_enabled        = true
      }

      "stop_instance" = {
        responder_rule_id = "STOP_INSTANCE"
        is_enabled        = true
      }

      "terminate_instance" = {
        responder_rule_id = "TERMINATE_INSTANCE"
        is_enabled        = true
      }

      "disable_iam_user" = {
        responder_rule_id = "DISABLE_IAM_USER"
        is_enabled        = true
      }

      "rotate_vault_key" = {
        responder_rule_id = "ROTATE_VAULT_KEY"
        is_enabled        = true
      }

      "delete_iam_policy" = {
        responder_rule_id = "DELETE_IAM_POLICY"
        is_enabled        = true
      }

      "enable_db_backup" = {
        responder_rule_id = "ENABLE_DB_BACKUP"
        is_enabled        = true
      }
    }
  }
}

