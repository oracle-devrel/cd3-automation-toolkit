// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create Default Route Table
############################

variable "manage_default_resource_id" {
  type    = string
  default = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "igw_id" {}
variable "ngw_id" {}
variable "sgw_id" {}
variable "drg_id" {}
variable "hub_lpg_id" {}
variable "spoke_lpg_id" {}
variable "exported_lpg_id" {}

variable "rt_details" {
  type = map(any)
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

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "network_entity_id" {
  type    = string
  default = null
}

variable "description" {
  type    = string
  default = null
}

variable "destination" {
  type    = string
  default = null
}

variable "destination_type" {
  type    = string
  default = null
}