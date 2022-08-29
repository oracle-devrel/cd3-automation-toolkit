// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Storage
# Create FSS
############################

variable "availability_domain" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "display_name" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "kms_key_id" {
  type    = string
  default = null
}

variable "source_snapshot_id" {
  type    = string
  default = null
}
