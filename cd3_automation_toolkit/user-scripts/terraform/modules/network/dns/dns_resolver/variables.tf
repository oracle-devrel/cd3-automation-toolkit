// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#############################
# Variable Block - DNS Zone #
#############################
variable "target_resolver_id" {
  type    = string
  default = null
}

variable "resolver_scope" {
  type    = string
  default = "PRIVATE"
}
variable "views" {
  type    = map(any)
  default = {}
}
variable "resolver_display_name" {
  type    = string
  default = null
}

variable "resolver_rules" {
  type    = map(any)
  default = null
}

variable "resolver_defined_tags" {
  type    = map(string)
  default = {}
}

variable "resolver_freeform_tags" {
  type    = map(string)
  default = {}
}

variable "endpoint_names" {
  type = map(any)
  default = {
    #    endpoint1 = {
    #    forwarding = true
    #    listening = false
    #    resolver_id = ""
    #    subnet_id = ""
    #    scope = "PRIVATE"
    #    endpoint_type = "VNIC"
    #    forwarding_address = null
    #    listening_address = null
    #    nsg_ids = []

  }


}