# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
