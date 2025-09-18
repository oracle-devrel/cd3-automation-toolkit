# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
