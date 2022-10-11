// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#####################################
# Variables Block - Dedicated VM Host
# Create Dedicated VM Hosts
#####################################

variable "availability_domain" {
  type    = string
  default = null
}
variable "compartment_id" {
  type    = string
  default = null
}
variable "vm_host_shape" {
  type    = string
  default = null
}
variable "defined_tags" {
  type    = map(string)
  default = {}
}
variable "freeform_tags" {
  type    = map(string)
  default = {}
}
variable "display_name" {
  type    = string
  default = null
}
variable "fault_domain" {
  type    = string
  default = null
}
