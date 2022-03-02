// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create NAT Gateway
############################

variable "compartment_id" {
  type    = string
  default = null
}

variable "vcn_id" {
  type    = string
  default = null
}

variable "public_ip_id" {
  type    = string
  default = null
}

variable "block_traffic" {
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

