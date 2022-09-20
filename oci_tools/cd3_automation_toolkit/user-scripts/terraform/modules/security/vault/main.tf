// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Resource Block - Security
## Create Vault
################################

resource "oci_kms_vault" "vault" {
  #Required
  compartment_id = var.compartment_id
  display_name   = var.display_name
  vault_type     = var.vault_type

  #Optional
  defined_tags  = var.defined_tags
  freeform_tags = var.freeform_tags

  lifecycle {
    ignore_changes = [defined_tags["Oracle-Tags.CreatedOn"], defined_tags["Oracle-Tags.CreatedBy"]]
  }
}
