# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Network
# Create VLANs
############################

variable "cidr_block" {
  description = "VLAN CIDR Block"
  type        = string
  default     = null
}
variable "compartment_id" {
  description = "VLAN Compartment"
  type        = string
  default     = null
}
variable "vcn_id" {
  description = "VLAN VCN ID"
  type        = string
  default     = null
}
variable "availability_domain" {
  type    = string
  default = null
}

variable "display_name" {
  description = "VLAN Display Name"
  type        = string
  default     = null
}
variable "nsg_ids" {
  description = "VLAN NSG ID"
  type        = list(string)
  default     = []
}
variable "route_table_id" {
  description = "VLAN Route Table ID"
  type        = string
  default     = null
}
variable "vlan_tag" {
  description = "VLAN Tag"
  type        = string
  default     = null
}
variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}

variable "network_compartment_id" {
  description = "Network compartmenet OCID to fetch NSG/Subnet details"
  type        = string
  default     = null
}


variable "vcn_names" {
  type    = list(any)
  default = []
}