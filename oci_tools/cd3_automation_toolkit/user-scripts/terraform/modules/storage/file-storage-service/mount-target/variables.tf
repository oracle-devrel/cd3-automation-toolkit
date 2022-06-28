// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Storage
# Create MTs
############################

variable "availability_domain" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "subnet_id" {
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

variable "hostname_label" {
  type    = string
  default = null
}

variable "ip_address" {
  type    = string
  default = null
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

variable "network_compartment_id" {}