data "oci_kms_vaults" "fw_vault" {
  compartment_id = var.compartment_id != null ? var.compartment_id : var.compartment_id
  filter {
    name   = "display_name"
    values = [var.vault_name]
  }
}

data "oci_vault_secrets" "fw_secret" {
  compartment_id = var.compartment_id != null ? var.compartment_id : var.compartment_id
  name = var.vault_secret_id
  vault_id = tostring(data.oci_kms_vaults.fw_vault.vaults[0].id)
}

locals {
  secret_ocid = tostring(data.oci_vault_secrets.fw_secret.secrets[0].id)

}