# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
}

resource "oci_kms_vault_replication" "vault_replication" {
  count           = var.replica_region != null ? 1 : 0
    #Required
  vault_id = oci_kms_vault.vault.id
  replica_region = var.replica_region
}