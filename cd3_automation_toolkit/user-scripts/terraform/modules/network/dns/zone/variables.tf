# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Variable Block - DNS Zone #
#############################
variable "zone_compartment_id" {
  type    = string
  default = null
}

variable "zone_name" {
  type    = string
  default = null
}
variable "zone_type" {
  type    = string
  default = null
}
variable "zone_scope" {
  type    = string
  default = null
}
variable "view_id" {
  type    = string
  default = null
}
variable "external_masters" {
  type    = map(any)
  default = {}
}

variable "zone_defined_tags" {
  type    = map(string)
  default = {}
}

variable "zone_freeform_tags" {
  type    = map(string)
  default = {}
}
