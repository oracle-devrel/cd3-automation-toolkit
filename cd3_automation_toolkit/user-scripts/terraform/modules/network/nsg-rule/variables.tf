# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Variable Block - Network
# Create Network Security Groups
#############################

variable "nsg_rules_details" {
  type    = map(any)
  default = {}
}

variable "key_name" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "nsg_id" {
  type    = string
  default = null
}

variable "source_type" {
  type    = string
  default = null
}

variable "direction" {
  type    = string
  default = null
}

variable "protocol" {
  type    = string
  default = null
}

variable "description" {
  type    = string
  default = null
}

variable "destination_addr" {
  type    = string
  default = null
}

variable "destination_type" {
  type    = string
  default = null
}

variable "source_addr" {
  type    = string
  default = null
}

variable "stateless" {
  type    = string
  default = null
}


