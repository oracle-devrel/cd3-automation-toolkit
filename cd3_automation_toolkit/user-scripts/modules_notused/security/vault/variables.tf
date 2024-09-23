# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Security
## Create Vault
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
  description = "User-friendly name to the Vault"
  type        = string
}

variable "replica_region" {
  description = "The region to be created replica to. When updated, replica will be deleted from old region, and created to updated region."
  type = string
}
