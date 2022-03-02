// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create DRG Route Distribution
############################

variable "distribution_type" {
  type    = string
  default = null
}

variable "drg_id" {
  type    = string
  default = null
}

variable "display_name" {
  type    = string
  default = null
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
