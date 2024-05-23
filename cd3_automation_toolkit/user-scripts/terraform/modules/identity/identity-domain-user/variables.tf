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
  description = "Family Name of the user"
  type        = string
  default     = "Default"
}

variable "idcs_endpoint" {
  description = "URL of the domain"
  type        = string
  default     = "https://idcs-domain-url"
}

variable "email" {
  type        = string
  description = "The email you assign to the User. Does not have to be unique, and it's changeable. "
  default     = null
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

variable "urnietfparamsscimschemasoracleidcsextensioncapabilities_user" {
  description = "A map of capabilities to disable."
  type = object({
    can_use_api_keys                 = bool
    can_use_auth_tokens              = bool
    can_use_console_password         = bool
    can_use_customer_secret_keys     = bool
    can_use_db_credentials           = bool
    can_use_oauth2client_credentials = bool
    can_use_smtp_credentials         = bool
  })
  default = {
    can_use_api_keys                 = true
    can_use_auth_tokens              = true
    can_use_console_password         = true
    can_use_customer_secret_keys     = true
    can_use_db_credentials           = true
    can_use_oauth2client_credentials = true
    can_use_smtp_credentials         = true
  }
}
