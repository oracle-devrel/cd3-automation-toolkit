// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Custom DHCP Options
############################

variable "compartment_id" {
  type    = string
  default = null
}

variable "type" {
  type    = string
  default = null
}

variable "option_type" {
  type    = string
  default = null
}

variable "server_type" {
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

variable "domain_name_type" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "vcn_id" {
  type    = string
  default = null
}

variable "custom_dns_servers" {
  type    = list(any)
  default = [""]
}

variable "search_domain_names" {
  type    = map(any)
  default = {}
}