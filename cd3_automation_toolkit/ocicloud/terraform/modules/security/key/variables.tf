# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
  default     = null
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

variable "rotation_interval_in_days"{
    description = "The interval of auto key rotation. For auto key rotation the interval should between 30 day and 365 days (1 year)."
    type        =  string
    default     =  "30"
}

variable "is_auto_rotation_enabled"{
    description = "A parameter specifying whether the auto key rotation is enabled or not."
    type        = bool
    default     = false
}