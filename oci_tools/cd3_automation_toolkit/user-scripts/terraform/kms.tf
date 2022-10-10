// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################################
# Module Block - Security
# Create KMS Vault and Key
############################################

module "vaults" {
  source   = "./modules/security/vault"
  for_each = var.vaults != null ? var.vaults : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags  = each.value.defined_tags
  display_name  = each.value.display_name
  freeform_tags = each.value.freeform_tags
  vault_type    = each.value.vault_type
}

module "keys" {
  source   = "./modules/security/key"
  for_each = var.keys != null ? var.keys : {}

  #Required
  compartment_id = each.value.compartment_id != null ? (length(regexall("ocid1.compartment.oc1*", each.value.compartment_id)) > 0 ? each.value.compartment_id : var.compartment_ocids[each.value.compartment_id]) : null

  #Optional
  defined_tags        = each.value.defined_tags
  display_name        = each.value.display_name
  freeform_tags       = each.value.freeform_tags
  algorithm           = each.value.algorithm != "" ? each.value.algorithm : "AES"
  length              = each.value.length != "" ? each.value.length : 32
  management_endpoint = merge(module.vaults.*...)[each.value.management_endpoint]["management_endpoint_tf_id"]
  protection_mode     = each.value.protection_mode
}