# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Variable Block - Network
# Create Subnets
#############################

variable "vcn_default_security_list_id" {}

variable "custom_security_list_id" {}

variable "tenancy_ocid" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "vcn_id" {
  type    = string
  default = null
}

variable "availability_domain" {
  type    = string
  default = null
}

variable "dhcp_options_id" {
  type    = string
  default = null
}

variable "prohibit_internet_ingress" {
  type    = bool
  default = false
}

variable "prohibit_public_ip_on_vnic" {
  type    = bool
  default = false
}

variable "route_table_id" {
  type    = string
  default = null
}

variable "security_list_ids" {
  type    = list(any)
  default = [""]
}

variable "ipv6cidr_block" {
  type    = string
  default = null
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

variable "dns_label" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}
