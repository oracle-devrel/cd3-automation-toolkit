# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Network
# Create VCNs
############################

variable "tenancy_ocid" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "cidr_blocks" {
  type    = list(any)
  default = [""]
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

variable "is_ipv6enabled" {
  type    = bool
  default = false
}

variable "ipv6private_cidr_blocks" {
  type    = list(any)
  default = []
}

variable "is_oracle_gua_allocation_enabled" {
  type    = bool
  default = false
}

variable "byoipv6cidr_details" {
  type    = list(any)
  default = [{}]
}
