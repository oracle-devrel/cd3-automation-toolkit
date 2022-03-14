#// Copyright (c) 2021, 2022, Oracle and/or its affiliates.
#
####################################
## Variables Block - Backup Policy
## Create Block Volume Backup Policy
####################################

variable "display_name" {
  description = "User-friendly name to the volume"
  type = string
  default = ""
}
variable "compartment_id" {
  description = "Compartment OCID to provision the volume"
  type = string
  default = ""
}
variable "block_tf_policy" {
  type = string
  default = ""
}
variable "policy_tf_compartment_id" {
  default = ""
}
variable "defined_tags" {
  description = "Defined tags for the volume"
  type = map(string)
}
variable "freeform_tags" {
  description = "Free-form tags for the volume"
  type = map(string)
}