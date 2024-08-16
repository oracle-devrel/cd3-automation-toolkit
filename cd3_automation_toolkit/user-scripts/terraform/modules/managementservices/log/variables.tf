# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
#############################
# Variable Block - Logging
# Create Log Groups and Logs
#############################

variable "tenancy_ocid" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}

variable "log_type" {
  type    = string
  default = null
}

variable "dhcp_options_id" {
  type    = string
  default = null
}

variable "description" {
  type    = string
  default = null
}


variable "log_group_id" {
  type    = string
  default = null
}

variable "source_category" {
  type    = string
  default = null
}

variable "source_resource" {
  type    = string
  default = null
}

variable "source_service" {
  type    = string
  default = null
}

variable "source_type" {
  type    = string
  default = null
}

variable "log_is_enabled" {
  type    = bool
  default = true
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

variable "log_retention_duration" {
  type    = number
  default = 30
}

variable "freeform_tags" {
  type    = map(any)
  default = {}
}
