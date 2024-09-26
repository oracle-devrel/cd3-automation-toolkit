# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
variable "compartment_id" {
  type = string
  default = null
  }

variable "network_compartment_id" {
  type = string
  default = null
  }


variable "subnet_id" {
  type = string
  default = null
}

variable "vcn_name" {
  type = string
  default = null
}
variable "network_firewall_policy_id" {
  type = string
  default = null
}

variable "display_name" {
  type = string
  default = null
}

variable "ipv4address" {
  type = string
  default = null
}
variable "ipv6address" {
  type = string
  default = null
}
variable "availability_domain" {
  type = string
  default = null
}
variable "network_security_group_ids" {
  type = list
  default = []
}
variable "nsg_id" {
  type = list
  default = []
}
variable "policy_id" {
  type = string
  default = null
}

variable "region" {
  type    = string
  default = null
}

variable "type" {
  type    = string
  default = null
}

variable "name" {
  type    = string
  default = null
}

variable "defined_tags" {
  type    = map(any)
  default = {}
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}
