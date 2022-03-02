// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Service Gateway
############################

variable "compartment_id" {
  type    = string
  default = null
}

variable "vcn_id" {
  type    = string
  default = null
}

variable "route_table_id" {
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

variable "service" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

