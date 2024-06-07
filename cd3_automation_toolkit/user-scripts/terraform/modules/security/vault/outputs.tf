// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################
## Outputs Block - Security
## Create Vault
################################

output "vault_tf_id" {
  value = oci_kms_vault.vault.id
}

output "management_endpoint_tf_id" {
  value = oci_kms_vault.vault.management_endpoint
}
