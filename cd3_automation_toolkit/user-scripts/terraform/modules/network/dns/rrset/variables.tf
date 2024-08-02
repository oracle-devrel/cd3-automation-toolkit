# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Variable Block - DNS Zone #
#############################
variable "rrset_compartment_id" {
  type    = string
  default = null
}

variable "rrset_domain" {
  type    = string
  default = null
}
variable "rrset_rtype" {
  type    = string
  default = null
}
variable "rrset_zone" {
  type    = string
  default = null
}

variable "rrset_ttl" {
  type    = number
  default = null
}
variable "rrset_rdata" {
  type    = list(any)
  default = []
}

variable "rrset_scope" {
  type    = string
  default = null
}

variable "rrset_view_id" {
  type    = string
  default = null
}
