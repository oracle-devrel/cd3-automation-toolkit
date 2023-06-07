// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Identity
# Create Users
############################

variable "tenancy_ocid" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "name" {
  type        = string
  description = "The name you assign to the user during creation. The name must be unique across all compartments in the tenancy."
  default     = null
}

variable "vcn_id" {
  type        = string
  description = "The id of the VCN."
  default     = null
}

variable "vcn_name" {
  type        = string
  description = "The name of the VCN."
  default     = null
}

variable "vcn_comp_map" {
  type        = map(any)
  description = "The name of the VCN."
  default     = null
}

variable "network_compartment_id" {
  type        = string
  description = "The OCID of the compartment that has Network components"
  default     = null
}

variable "public_source_list" {
  type        = list(string)
  description = "The list of public source for network sources"
  default     = []
}

variable "virtual_source_list" {
  type        = map(any)
  description = "The list of VCN for network sources"
  default     = {}
}

variable "description" {
  type        = string
  description = "The description you assign to the User. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "cidr_blocks" {
  type        = string
  description = "VCN CIDR Block"
  default     = null
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