# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################################
# Module Block - Security
# Create KMS Vault and Key
############################################

module "vaults" {
  source   = "./modules/security/vault"
  for_each = var.vaults != null ? var.vaults : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags   = each.value.defined_tags
  display_name   = each.value.display_name
  freeform_tags  = each.value.freeform_tags
  vault_type     = each.value.vault_type
  replica_region = each.value.replica_region
}

module "keys" {
  source   = "./modules/security/key"
  for_each = var.keys != null ? var.keys : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags              = each.value.defined_tags
  display_name              = each.value.display_name
  freeform_tags             = each.value.freeform_tags
  algorithm                 = each.value.algorithm != null ? each.value.algorithm : "AES"
  length                    = each.value.length != null ? each.value.length : 32
  curve_id                  = each.value.curve_id != null ? each.value.curve_id : null
  management_endpoint       = merge(module.vaults.*...)[each.value.vault_name]["management_endpoint_tf_id"]
  protection_mode           = each.value.protection_mode
  is_auto_rotation_enabled  = each.value.is_auto_rotation_enabled
  rotation_interval_in_days = each.value.rotation_interval_in_days != null ? each.value.rotation_interval_in_days : 60
}