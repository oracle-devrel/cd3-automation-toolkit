# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
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
variable "user_id" {
  description = "email id of the user"
  type        = string
  default     = null
}

variable "description" {
  type        = string
  description = "The description of the user."
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

variable "groups" {
  type        = list(string)
  description = "The name of the group user is member of."
  default     = []
}


variable "family_name" {
  description = "Last Name of the user"
  type        = string
  default     = "Default"
}

variable "given_name" {
  description = "First Name of the user"
  type        = string
  default     = "Default"
}

variable "display_name" {
  description = "Display Name of the user"
  type        = string
  default     = "Default"
}

variable "identity_domain" {
default = {}
}

variable "email" {
  type        = string
  description = "The email you assign to the User. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "home_phone_number" {
  type        = string
  description = "Home phone number of the user"
  default     = null
}

variable "mobile_phone_number" {
  type        = string
  description = "Mobile phone number of the user"
  default     = null
}

variable "recovery_email" {
  type        = string
  description = "The recovery email you assign to the User. It's changeable. "
  default     = null
}

variable "enabled_capabilities" {
  type        = list(string)
  description = "The name of the capabilities enabled for user"
  default     = []
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

variable "honorific_prefix" {
  type    = string
  default = ""
}

variable "middle_name" {
  type    = string
  default = ""
}


