# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Load Balancer
# Create Load Balancer
############################

variable "compartment_id" {
  type        = string
  description = "The OCID of the compartment"
  default     = null
}

variable "network_compartment_id" {
  type        = string
  description = "The OCID of the compartment that has Network components"
  default     = null
}

variable "display_name" {
  type        = string
  description = "The display name of the load balancer"
  default     = null
}

variable "shape" {
  type        = string
  description = "Load Balancer shape - Allowed values: 100Mbps|10Mbps|10Mbps-Micro|400Mbps|8000Mbps|flexible "
  default     = "100Mbps" #Default value as per hashicorp terraform
}

variable "subnet_ids" {
  type        = list(any)
  description = "Subnets to place the load balancer in"
  default     = []
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "ip_mode" {
  type        = string
  description = "Whether the load balancer has an IPv4 or IPv6 IP address"
  default     = "IPV4" #Default value as per hashicorp terraform
}

variable "is_private" {
  type        = bool
  description = "Whether the load balancer has a VCN-local (private) IP address. If True , Load Balancer is private, else it's public"
  default     = "false" #Default value as per hashicorp terraform; Creates a Public Load Balancer
}

variable "network_security_group_ids" {
  type        = list(any)
  description = "NSGs to place the load balancer in"
  default     = []
}

variable "key_name" {
  type    = string
  default = null
}

variable "vcn_names" {
  type    = list(any)
  default = []
}

variable "load_balancers" {}

variable "reserved_ips_id" {
  type    = list(any)
  default = []
}