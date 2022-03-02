// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Identity
# Create Groups
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy."
  default     = null
}

variable "group_name" {
  type        = string
  description = "The name you assign to the group during creation. The name must be unique across all compartments in the tenancy."
  default     = null
}

// The description is only used if group_create = true.
variable "group_description" {
  type        = string
  description = "The description you assign to the Group. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "group_create" {
  type        = bool
  description = "(Deprecated) Create the group or not. If true, the user must have permissions to create the group; If false, group data will be returned about the group if it exists, if not found, then an empty string will be returned for the group ID."
  default     = true
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