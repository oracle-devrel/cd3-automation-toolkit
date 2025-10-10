# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Network
# Create Route Table
############################

variable "compartment_id" {
  type    = string
  default = null
}

variable "vcn_id" {
  type    = string
  default = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "igw_id" {
    type    = map(any)
    default = {}
}
variable "ngw_id" {
    type    = map(any)
    default = {}
}
variable "sgw_id" {
    type    = map(any)
    default = {}
}
variable "drg_id" {
    type    = map(any)
    default = {}
}
variable "hub_lpg_id" {
    type    = map(any)
    default = {}
}
variable "spoke_lpg_id" {
    type    = map(any)
    default = {}
}
variable "peer_lpg_id" {
    type    = map(any)
    default = {}
}
variable "exported_lpg_id" {
    type    = map(any)
    default = {}
}
variable "none_lpg_id" {
    type    = map(any)
    default = {}
}

variable "rt_details" {
  type = map(any)
}

variable "cidr_block" {
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

variable "network_entity_id" {
  type    = string
  default = null
}

variable "description" {
  type    = string
  default = null
}

variable "destination" {
  type    = string
  default = null
}

variable "destination_type" {
  type    = string
  default = null
}

variable "gateway_route_table" {
  type    = bool
  default = false
}

variable "default_route_table" {
  type    = bool
  default = false
}


variable "manage_default_resource_id" {
  type    = string
  default = null
}