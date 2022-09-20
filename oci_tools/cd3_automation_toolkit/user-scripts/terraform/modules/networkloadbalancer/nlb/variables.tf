// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#########################################
# Variable Block - Network Load Balancer
# Create Network Load Balancer
#########################################

variable "compartment_id" {
  type    = string
  default = null
}

variable "network_compartment_id" {}

variable "subnet_id" {
  type    = string
  default = null
}

variable "vcn_name" {
  type    = string
  default = null
}

variable "display_name" {
  type    = string
  default = null
}

variable "is_preserve_source_destination" {
  type    = bool
  default = false
}

variable "is_private" {
  type    = bool
  default = true
}

variable "network_security_group_ids" {
  type        = list(any)
  description = "NSGs to place the load balancer in"
  default     = []
}

variable "nlb_ip_version" {
  type    = string
  default = null
}

variable "reserved_ips_id" {
  type    = list(any)
  default = []
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