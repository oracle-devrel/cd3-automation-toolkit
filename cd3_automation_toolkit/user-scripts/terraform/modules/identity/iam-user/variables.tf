// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variables Block - Identity
# Create Users
############################

variable "tenancy_ocid" {
  type    = string
  default = null
}

variable "compartment_id" {
  type    = string
  default = null
}


variable "user_name" {
  type        = string
  description = "The name you assign to the user during creation. The name must be unique across all compartments in the tenancy."
  default     = null
}

variable "group_name" {
  type        = string
  description = "The name of the group."
  default     = null
}

variable "group_id" {
  type        = string
  description = "The id of the group."
  default     = null
}

variable "group_membership" {
  type        = list(string)
  description = "The name of the group user is member of."
  default     = []
}

variable "user_description" {
  type        = string
  description = "The description you assign to the User. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "user_email" {
  type        = string
  description = "The email you assign to the User. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "disable_capabilities" {
  type        = list(string)
  description = "The name of the capabilities disabled for user"
  default     = []
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


variable "group_ids" {
  type    = list(string)
  default = []
}