// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

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
  type = list(object({
    type  = string
    value = string
  }))
  default = []
}

variable "emails" {
  description = "List of email ids of the users"
  type        = list(string)
}


variable "idcs_endpoint" {
  description = "URL of the domain"
  type        = string
  default     = "https://idcs-domain-url"
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

