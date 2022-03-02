// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Dynamic Routing Gateway
############################

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

variable "drg_route_table_id" {
  type    = string
  default = null
}

variable "vcn_route_table_id" {
  type    = string
  default = null
}

variable "network_details_id" {
  type    = string
  default = null
}

variable "network_details_type" {
  type    = string
  default = null
}

