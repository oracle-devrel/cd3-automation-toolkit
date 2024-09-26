# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Storage
# Create FSS Replication
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

variable "display_name" {
  type    = string
  default = null
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}

variable "source_id" {
  type    = string
  default = null
}

variable "target_id" {
  type    = string
  default = null
}

variable "replication_interval" {
  type    = number
  default = 60
}
