// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#################################
## Variables Block - Security
## Create Key
#################################

variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type        = string
}

variable "vault_type" {
  description = "The type of vault to create"
  type        = string
  default     = null
}

variable "algorithm" {
  description = "The algorithm used by a key's key versions to encrypt or decrypt."
  type        = string
  default     = "AES"
}

variable "length" {
  description = "The length of the key in bytes, expressed as an integer. Supported values include the following: AES: 16, 24, or 32 RSA: 256, 384, or 512 ECDSA: 32, 48, or 66"
  type        = number
  default     = 256
}

variable "curve_id" {
  description = "Supported curve IDs for ECDSA keys."
  type        = string
  default     = false
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "display_name" {
  description = "User-friendly name to the Key"
  type        = string
}

variable "protection_mode" {
  description = "The key's protection mode indicates how the key persists and where cryptographic operations that use the key are performed."
  type        = string
  default     = "HSM"
}

variable "management_endpoint" {
  description = "Vault ID"
  type        = string
  default     = null
}