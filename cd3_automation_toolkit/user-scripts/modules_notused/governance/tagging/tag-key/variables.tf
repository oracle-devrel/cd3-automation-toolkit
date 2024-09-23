# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl.
#
############################
# Variable Block - Governance
# Create Tag Key
############################

variable "tenancy_ocid" {
  type        = string
  description = "The OCID of the tenancy."
  default     = null
}

variable "compartment_id" {
  type        = string
  description = "The OCID of the parent compartment containing the compartment. Allow for sub-compartments creation"
  default     = null
}

variable "tag_keys" {}

variable "key_name" {}

variable "is_cost_tracking" {
  type        = bool
  description = "Indicates whether the tag is enabled for cost tracking."
}

variable "tag_namespace_id" {
  type        = string
  description = "The OCID of the Tag Namespace"
  default     = null
}

variable "description" {
  type        = string
  description = "The description you assign to the tag key. Does not have to be unique, and it's changeable. "
  default     = null
}

variable "name" {
  type        = string
  description = "Tag name"
  default     = null
}

variable "is_retired" {
  type        = bool
  description = "Enable to retire the tag key."
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

