// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Network
# Create DRG Route Rule
############################

variable "drg_route_table_id" {
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

variable "next_hop_drg_attachment_id" {
  type    = string
  default = null
}