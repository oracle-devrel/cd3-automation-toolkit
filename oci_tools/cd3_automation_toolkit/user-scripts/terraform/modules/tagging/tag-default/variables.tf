// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Variable Block - Governance
# Create Tag Defaults
############################

variable "compartment_id" {
  type        = string
  description = "The OCID of the compartment"
  default     = null
}

variable "tag_definition_id" {
  type        = string
  description = "The OCID of the Tag Definition that must be made default"
  default     = null
}

variable "value" {
  type        = string
  description = "The default value for the tag"
  default     = null
}

variable "is_required" {
  type        = bool
  description = "If true, a value is set during resource creation (either by the user creating the resource or another tag defualt). If no value is set, resource creation is blocked."
}

