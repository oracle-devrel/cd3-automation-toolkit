// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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

variable "is_ipv6enabled" {
  type    = bool
  default = "false"
}
