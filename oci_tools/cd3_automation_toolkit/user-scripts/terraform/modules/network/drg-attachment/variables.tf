// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
############################
# Variable Block - Network
# Create Dynamic Routing Gateway Attachment
############################
variable "compartment_id" {
  type    = string
  default = null
}
variable "defined_tags" {
  type = map(any)
  default = { "Oracle-Tags.CreatedOn" = "$${oci.datetime}",
    "Oracle-Tags.CreatedBy" = "$${iam.principal.name}"
  }
}
variable "drg_display_name" {
  type    = string
  default = null
}
variable "freeform_tags" {
  type    = map(any)
  default = {}
}
variable "drg_route_table_id" {
  type    = string
  default = null
}
variable "vcn_route_table_id" {
  type    = string
  default = null
}
variable "drg_attachments" {}

variable "vcns_tf_id" {}

variable "route_table_tf_id" {}

variable "default_route_table_tf_id" {}

variable "drg_id" {
  type    = string
  default = null
}
variable "key_name" {
  type    = string
  default = null
}