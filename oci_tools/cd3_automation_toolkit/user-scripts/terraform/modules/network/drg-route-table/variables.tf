// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create DRG Route Table
############################

variable "drg_id" {
  type    = string
  default = null
}

variable "import_drg_route_distribution_id" {
  type    = string
  default = null
}

variable "is_ecmp_enabled" {
  type    = bool
  default = false
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