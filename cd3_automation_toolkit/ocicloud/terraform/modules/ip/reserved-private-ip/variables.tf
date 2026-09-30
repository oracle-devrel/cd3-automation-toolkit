# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#################################
## Variables Block - Secondary Private IP
## Create Secondary Private IP
#################################

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the volume"
  type        = map(string)
}

variable "lifetime" {
  type    = string
  default = "RESERVED"
}

variable "network_compartment_id" {
  type    = string
  default = null
}

variable "display_name" {
  description = "User-friendly name to the volume"
  type        = string
}

variable "vcn_name" {
  type    = string
  default = null
}

variable "subnet_id" {
  type        = string
  description = "Subnets to place the private IPs in"
  default     = null
}

variable "vnic_id" {
  type    = string
  default = null
}

variable "hostname_label" {
  type    = string
  default = null
}

variable "ip_address" {
  type    = string
  default = null
}

variable "vlan_id" {
  type    = string
  default = null
}
