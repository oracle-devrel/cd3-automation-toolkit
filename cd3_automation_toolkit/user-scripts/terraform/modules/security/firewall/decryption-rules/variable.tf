# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
variable "compartment_id" {
   type = string
  default = null
}
variable "subnet_name" {
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

variable "icmp_type" {
  type = number
  default = null

}

variable "icmp_code" {
  type = number
  default = null
}
variable "minimum_port" {
  type = number
  default = null
}

variable "maximum_port" {
  type = number
  default = null
}

variable "service_name" {
   type = string
  default = null
}

variable "service_type" {
   type = string
  default = null
}

variable "region" {
  type    = string
  default = "us-ashburn-1"
}

variable "type" {
  type    = string
  default = null
}

variable "name" {
  type    = string
  default = null
}

variable "policy" {
  type    = map(any)
  default = {}
}

variable "service_port_ranges" {
  type    = map(any)
  default = {}
}

variable "key_name" {
  type    = string
  default = null
}

variable "rule_condition" {
  type    = map(any)
  default = {}
}
variable "rule_position" {
  type    = map(any)
  default = {}
}
variable "key_name1" {
  type    = string
  default = null
}

variable "key_name2" {
  type    = string
  default = null
}

variable "rule_name" {
  type    = string
  default = null
}

variable "action" {
  type    = string
  default = null
}
variable "application" {
  type    = list(string)
  default = []
}
variable "destination_address" {
  type    = list(string)
  default = []
}
variable "source_address" {
  type    = list(string)
  default = []
}
variable "url" {
  type    = list(string)
  default = []
}
variable "service" {
   type = list(string)
  default = []
}

variable "after_rule" {
  type    = string
  default = null
}
variable "before_rule" {
  type    = string
  default = null
}
variable "inspection" {
  type    = string
  default = null
}
variable "secret" {
  type    = string
  default = null
}
variable "decryption_profile" {
  type    = string
  default = null
}



