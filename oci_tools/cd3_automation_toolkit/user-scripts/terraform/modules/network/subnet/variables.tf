// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#############################
# Variable Block - Network
# Create Subnets
#############################

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
  type    = list
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

variable "cidr_blocks" {
  type    = list
  default = [""]
}

variable "defined_tags" {
  type    = map
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
              "Oracle-Tags.CreatedBy"= "$${iam.principal.name}"
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
  type    = map
  default = {}
}
