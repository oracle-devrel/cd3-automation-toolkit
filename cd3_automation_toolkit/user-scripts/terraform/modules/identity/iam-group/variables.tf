# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Identity
# Create Groups
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy."
  default     = null
}

variable "members" {
  description = "List of members"
  type = list(string)
  default = []
}

variable "group_membership" {
  type        = list(string)
  description = "The name of the group user is member of."
  default     = []
}

variable "group_name" {
  type        = string
  description = "The name you assign to the group during creation. The name must be unique across all compartments in the tenancy."
  default     = null
}

variable "group_description" {
  type        = string
  description = "The description you assign to the Group. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "matching_rule" {
  type    = string
  default = ""
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