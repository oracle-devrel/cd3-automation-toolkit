// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

#################################
## Variables Block - Secondary Private IP
## Create Secondary Private IP
#################################

variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type        = map(string)
}

variable "defined_tags" {
  description = "Defined tags for the volume"
  type        = map(string)
}

variable "display_name" {
  description = "User-friendly name to the volume"
  type        = string
}

variable "vnic_id" {
  type    = string
  default = null
}

variable "hostname_label" {
  type    = string
  default = null
}

variable "ip_address" {
  type    = string
  default = null
}

variable "vlan_id" {
  type    = string
  default = null
}
