# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variables Block - Identity
# Create Groups
############################

variable "compartment_id" {
  description = "The compartment ID information"
  type        = string
  default     = null
}

variable "user_id" {
  description = "Id of the user"
  type        = string
  default     = null
}

variable "members" {
  description = "List of email ids of the users"
  type        = list(string)
}


variable "identity_domain" {
default = {}
}


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

variable "group_description" {
  type        = string
  description = "The description you assign to the Group. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "matching_rule" {
  type    = string
  description = "The matching rule associated with the dynamic group"
  default = ""
}

variable "defined_tags" {
  description = "Defined tags for the group"
  type        = list(object({
    key       = string
    namespace = string
    value     = string
  }))
  default     = []
}

variable "freeform_tags_key" {
  type    = string
  default = ""
}

variable "freeform_tags_value" {
  type    = string
  default = ""
}

variable "user_can_request_access" {
  type    = bool
  description = "Specifies whether user can request access to the group"
  default = false

}
