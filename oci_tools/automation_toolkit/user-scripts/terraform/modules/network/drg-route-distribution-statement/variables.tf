// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

################################################
# Variable Block - Network
# Create DRG Route Distribution Statement
################################################

variable "drg_route_distribution_id" {
  type    = string
  default = null
}

variable "key_name" {
  type    = string
  default = null
}

variable "action" {
  type    = string
  default = null
}

variable "priority" {
  type    = number
  default = null
}

variable "drg_route_distribution_statements" {
  type    = map(any)
  default = {}
}

variable "drg_attachment_ids" {}
