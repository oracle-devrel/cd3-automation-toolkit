// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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


